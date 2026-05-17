from app.schemas.documents import RagAskRequest, RagAskResponse
from app.core.security import CurrentUser
from app.services.document_store import DOCUMENT_STORE
from app.services.llm import ChatProviderError, FallbackChatProvider
from app.services.seed_corpus import ensure_seed_corpus


class RagService:
    def ask(self, request: RagAskRequest, user: CurrentUser) -> RagAskResponse:
        ensure_seed_corpus()
        chunks = DOCUMENT_STORE.search(
            query=request.question,
            user=user,
            plant_id=request.plant_id,
            top_k=request.top_k,
        )
        if not chunks:
            return RagAskResponse(
                answer="No relevant evidence was found. Escalate to a supervisor before taking action.",
                recommendation="Do not issue a machine recommendation without supporting SOP or work-order evidence.",
                urgency="unknown",
                next_steps=["Escalate to a supervisor.", "Upload or select relevant SOP evidence.", "Retry the query."],
                citations=[],
                retrieved_chunks=[],
                model_used="retrieval-only",
                fallback_used=True,
                confidence_notes="No evidence available.",
            )

        provider = FallbackChatProvider()
        try:
            grounded = provider.answer(request.question, chunks)
        except ChatProviderError:
            return RagAskResponse(
                answer="Evidence was retrieved, but no model provider was available. Review the cited chunks before action.",
                recommendation="Review retrieved evidence manually before creating work orders.",
                urgency="review",
                next_steps=["Read the cited chunks.", "Confirm machine state.", "Retry when a provider is available."],
                citations=chunks,
                retrieved_chunks=chunks,
                model_used="retrieval-only",
                fallback_used=True,
                confidence_notes="Provider fallback exhausted; retrieval-only response returned.",
            )

        return RagAskResponse(
            answer=grounded.answer,
            recommendation=grounded.recommendation,
            urgency=grounded.urgency,
            next_steps=grounded.next_steps,
            citations=chunks,
            retrieved_chunks=chunks,
            model_used=grounded.model_used,
            fallback_used=provider.fallback_used,
            confidence_notes="Answer generated only from retrieved evidence chunks. If evidence is thin, escalate.",
        )
