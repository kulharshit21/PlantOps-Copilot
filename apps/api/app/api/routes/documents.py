from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, get_current_user
from app.schemas.documents import DocumentIngestRequest, DocumentIngestResponse, DocumentRead, RetrievedChunk
from app.services.audit import AuditLogService
from app.services.chunking import TextChunker
from app.services.document_store import DOCUMENT_STORE
from app.services.embeddings import MockEmbeddingProvider
from app.services.seed_corpus import ensure_seed_corpus
from app.services.supabase import SupabaseService, SupabaseServiceError

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
def list_documents(
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> list[DocumentRead]:
    try:
        return SupabaseService(settings).list_documents(user)
    except SupabaseServiceError as exc:
        if settings.demo_mode:
            ensure_seed_corpus()
            return DOCUMENT_STORE.list_documents(user)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase documents data is unavailable",
        ) from exc


@router.post("/ingest", response_model=DocumentIngestResponse)
def ingest_document(
    request: DocumentIngestRequest,
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> DocumentIngestResponse:
    try:
        service = SupabaseService(settings)
        plant_id = request.plant_id or user.plant_id
        document = service.create_document(
            user,
            title=request.title,
            document_type=request.document_type,
            source_uri=request.source_uri,
            plant_id=plant_id,
        )
        chunker = TextChunker()
        embedding_provider = MockEmbeddingProvider(dimensions=768)
        source_uri = request.source_uri or f"supabase://documents/{document.id}"
        chunk_payloads = [
            {
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "source_page": chunk.source_page,
                "source_uri": source_uri,
                "citation_label": f"{request.title}#chunk-{chunk.chunk_index}",
                "embedding": embedding_provider.embed(chunk.content),
                "metadata": {"provider": "deterministic-local"},
            }
            for chunk in chunker.chunk(request.content)
        ]
        chunks: list[RetrievedChunk] = service.create_document_chunks(
            user,
            document_id=document.id,
            title=request.title,
            chunks=chunk_payloads,
            plant_id=plant_id,
        )
        service.create_audit_log(
            user,
            action="document.ingest",
            entity_type="document",
            entity_id=document.id,
            details={"chunk_count": len(chunks), "document_type": request.document_type},
            plant_id=plant_id,
        )
        return DocumentIngestResponse(document=document, chunk_count=len(chunks), chunks=chunks)
    except SupabaseServiceError as exc:
        if not settings.demo_mode:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Supabase document ingestion is unavailable",
            ) from exc

        response = DOCUMENT_STORE.ingest(request, user)
        AuditLogService().record(
            actor_id=user.user_id,
            action="document.ingest",
            resource_type="document",
            resource_id=response.document.id,
            metadata={"chunk_count": response.chunk_count, "document_type": request.document_type},
        )
        return response
