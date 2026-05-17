from time import perf_counter

from app.core.config import Settings, get_settings
from app.schemas.documents import RagAskRequest, RagAskResponse
from app.core.security import CurrentUser
from app.services.document_store import DOCUMENT_STORE
from app.services.embeddings import (
    EmbeddingProviderError,
    LocalOllamaEmbeddingProvider,
    MistralEmbeddingProvider,
    MockEmbeddingProvider,
)
from app.services.llm import ChatProviderError, FallbackChatProvider
from app.services.seed_corpus import ensure_seed_corpus
from app.services.supabase import SupabaseService, SupabaseServiceError


class RagServiceError(RuntimeError):
    pass


class RagService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def ask(self, request: RagAskRequest, user: CurrentUser) -> RagAskResponse:
        started = perf_counter()
        service = SupabaseService(self.settings)
        try:
            query_embedding = self._embed_query(request.question)
            chunks = service.match_document_chunks(
                user,
                query_embedding=query_embedding,
                plant_id=request.plant_id,
                top_k=request.top_k,
            )
        except (SupabaseServiceError, EmbeddingProviderError) as exc:
            if not self.settings.demo_mode:
                raise RagServiceError("Live RAG retrieval is unavailable") from exc
            ensure_seed_corpus()
            chunks = DOCUMENT_STORE.search(
                query=request.question,
                user=user,
                plant_id=request.plant_id,
                top_k=request.top_k,
            )

        if not chunks:
            response = RagAskResponse(
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
            self._persist_rag(service, user, request, response, started)
            return response

        provider = FallbackChatProvider()
        try:
            grounded = provider.answer(request.question, chunks)
        except ChatProviderError:
            response = RagAskResponse(
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
            self._persist_rag(service, user, request, response, started)
            return response

        response = RagAskResponse(
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
        self._persist_rag(service, user, request, response, started)
        return response

    def _embed_query(self, question: str) -> list[float]:
        if self.settings.demo_mode:
            return MockEmbeddingProvider(dimensions=768).embed(question)
        providers = []
        if self.settings.mistral_api_key is not None:
            providers.append(MistralEmbeddingProvider())
        providers.append(LocalOllamaEmbeddingProvider())
        errors: list[str] = []
        for provider in providers:
            try:
                embedding = provider.embed(question)
                if len(embedding) != 768:
                    raise EmbeddingProviderError("Embedding provider returned a non-768-dimensional vector")
                return embedding
            except EmbeddingProviderError as exc:
                errors.append(str(exc))
        raise EmbeddingProviderError("; ".join(errors))

    def _persist_rag(
        self,
        service: SupabaseService,
        user: CurrentUser,
        request: RagAskRequest,
        response: RagAskResponse,
        started: float,
    ) -> None:
        citations = [
            {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "title": chunk.title,
                "source_uri": chunk.source_uri,
                "source_page": chunk.source_page,
                "score": chunk.score,
            }
            for chunk in response.citations
        ]
        latency_ms = int((perf_counter() - started) * 1000)
        try:
            service.create_rag_query(
                user,
                query=request.question,
                answer=response.answer,
                citations=citations,
                model_used=response.model_used,
                fallback_used=response.fallback_used,
                latency_ms=latency_ms,
                plant_id=request.plant_id,
            )
            service.create_audit_log(
                user,
                action="rag.ask",
                entity_type="rag_query",
                details={
                    "citation_count": len(citations),
                    "model_used": response.model_used,
                    "fallback_used": response.fallback_used,
                    "latency_ms": latency_ms,
                },
                plant_id=request.plant_id,
            )
        except SupabaseServiceError as exc:
            if not self.settings.demo_mode:
                raise RagServiceError("RAG persistence failed") from exc
