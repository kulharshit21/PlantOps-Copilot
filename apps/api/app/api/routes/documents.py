from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.documents import DocumentIngestRequest, DocumentIngestResponse, DocumentRead
from app.services.audit import AuditLogService
from app.services.document_store import DOCUMENT_STORE
from app.services.seed_corpus import ensure_seed_corpus

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentRead])
def list_documents(user: CurrentUser = Depends(get_current_user)) -> list[DocumentRead]:
    ensure_seed_corpus()
    return DOCUMENT_STORE.list_documents(user)


@router.post("/ingest", response_model=DocumentIngestResponse)
def ingest_document(
    request: DocumentIngestRequest,
    user: CurrentUser = Depends(get_current_user),
) -> DocumentIngestResponse:
    response = DOCUMENT_STORE.ingest(request, user)
    AuditLogService().record(
        actor_id=user.user_id,
        action="document.ingest",
        resource_type="document",
        resource_id=response.document.id,
        metadata={"chunk_count": response.chunk_count, "document_type": request.document_type},
    )
    return response
