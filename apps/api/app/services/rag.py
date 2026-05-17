from app.schemas.documents import RagAskRequest, RagAskResponse
from app.services.demo_data import DEMO_CHUNKS


class RagService:
    def ask(self, request: RagAskRequest) -> RagAskResponse:
        chunks = DEMO_CHUNKS[: request.top_k]
        if not chunks:
            return RagAskResponse(
                answer="No relevant evidence was found. Escalate to a supervisor before taking action.",
                citations=[],
                retrieved_chunks=[],
                model_used="retrieval-only",
                fallback_used=True,
                confidence_notes="No evidence available.",
            )

        return RagAskResponse(
            answer=(
                "Recommendation: pause the job, inspect tool holder runout and lubrication, "
                "then schedule bearing inspection under lockout/tagout controls."
            ),
            citations=chunks,
            retrieved_chunks=chunks,
            model_used="mock-grounded-demo",
            fallback_used=False,
            confidence_notes="Grounded in demo SOP chunks; full LLM provider arrives in RAG phase.",
        )
