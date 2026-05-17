from abc import ABC, abstractmethod
import json
from urllib import error, request

from app.core.config import get_settings
from app.schemas.documents import RetrievedChunk


class ChatProviderError(RuntimeError):
    pass


class GroundedAnswer:
    def __init__(
        self,
        *,
        answer: str,
        recommendation: str,
        urgency: str,
        next_steps: list[str],
        model_used: str,
    ) -> None:
        self.answer = answer
        self.recommendation = recommendation
        self.urgency = urgency
        self.next_steps = next_steps
        self.model_used = model_used


class ChatProvider(ABC):
    @abstractmethod
    def answer(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswer:
        raise NotImplementedError


class MockChatProvider(ChatProvider):
    def answer(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswer:
        _ = question
        chunk_ids = ", ".join(chunk.chunk_id for chunk in chunks[:3])
        recommendation = (
            "Pause the Line 2 spindle job, inspect tool holder runout and lubrication, "
            "then schedule bearing inspection before the next shift."
        )
        next_steps = [
            "Stop at the next safe pause and capture torque, vibration, and tool-wear readings.",
            "Apply lockout/tagout before opening guards or inspecting the spindle housing.",
            "Replace or inspect the tool holder, verify lubrication, and check bearing noise.",
            "Create a high-priority work order with cited SOP evidence.",
        ]
        return GroundedAnswer(
            answer=f"{recommendation} Evidence chunks used: {chunk_ids}.",
            recommendation=recommendation,
            urgency="high",
            next_steps=next_steps,
            model_used="mock-chat-grounded-v1",
        )


class MistralChatProvider(ChatProvider):
    def answer(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswer:
        _ = question
        _ = chunks
        raise ChatProviderError("Mistral provider not configured; missing server-side API key.")


class OllamaChatProvider(ChatProvider):
    def answer(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswer:
        settings = get_settings()
        evidence = "\n\n".join(
            f"[{chunk.chunk_id}] {chunk.title}: {chunk.content}" for chunk in chunks
        )
        prompt = (
            "Answer only from evidence. Return concise maintenance recommendation, urgency, and next steps.\n\n"
            f"Question: {question}\n\nEvidence:\n{evidence}"
        )
        payload = {
            "model": settings.ollama_llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        http_request = request.Request(
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with request.urlopen(http_request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (OSError, error.HTTPError, json.JSONDecodeError) as exc:
            raise ChatProviderError(f"Ollama provider unavailable: {exc.__class__.__name__}") from exc

        content = data.get("message", {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise ChatProviderError("Ollama provider returned an empty message.")

        return GroundedAnswer(
            answer=content.strip(),
            recommendation=content.strip().splitlines()[0][:500],
            urgency="review",
            next_steps=[
                "Review the cited chunks before acting.",
                "Confirm telemetry with the shift supervisor.",
                "Draft or approve work order only after human review.",
            ],
            model_used=f"ollama:{settings.ollama_llm_model}",
        )


class FallbackChatProvider(ChatProvider):
    def __init__(self, providers: list[ChatProvider] | None = None) -> None:
        self.providers = providers or [MistralChatProvider(), OllamaChatProvider(), MockChatProvider()]
        self.fallback_used = False

    def answer(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswer:
        errors: list[str] = []
        self.fallback_used = False
        for index, provider in enumerate(self.providers):
            try:
                answer = provider.answer(question, chunks)
                self.fallback_used = index > 0
                return answer
            except ChatProviderError as exc:
                errors.append(str(exc))
        raise ChatProviderError("; ".join(errors))
