from app.schemas.documents import RagAskRequest, RagAskResponse
from app.core.security import CurrentUser
from app.services.document_store import DOCUMENT_STORE
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
            model_used="retrieval-grounded-demo",
            fallback_used=False,
            confidence_notes="Grounded in retrieved seed corpus chunks; full LLM provider arrives next.",
        )
