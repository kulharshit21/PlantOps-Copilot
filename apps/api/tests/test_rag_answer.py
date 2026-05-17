from app.schemas.documents import RetrievedChunk
from app.services.llm import ChatProviderError, FallbackChatProvider, GroundedAnswer, MockChatProvider


class FailingProvider:
    def answer(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswer:
        _ = question
        _ = chunks
        raise ChatProviderError("failed")


def test_mock_answer_includes_citation_ids() -> None:
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        title="SOP",
        content="Inspect spindle vibration.",
        source_uri="seed://sop",
    )

    answer = MockChatProvider().answer("What now?", [chunk])

    assert "chunk-1" in answer.answer
    assert answer.recommendation
    assert answer.next_steps


def test_provider_fallback_uses_second_provider() -> None:
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        title="SOP",
        content="Inspect spindle vibration.",
        source_uri="seed://sop",
    )
    provider = FallbackChatProvider(providers=[FailingProvider(), MockChatProvider()])

    answer = provider.answer("What now?", [chunk])

    assert answer.model_used == "mock-chat-grounded-v1"
    assert provider.fallback_used is True
