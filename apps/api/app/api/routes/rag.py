from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.documents import RagAskRequest, RagAskResponse
from app.services.audit import AuditLogService
from app.services.rag import RagService

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/ask", response_model=RagAskResponse)
def ask_rag(
    request: RagAskRequest,
    user: CurrentUser = Depends(get_current_user),
) -> RagAskResponse:
    AuditLogService().record(
        actor_id=user.user_id,
        action="rag.ask",
        resource_type="rag_query",
        metadata={"question_length": len(request.question), "top_k": request.top_k},
    )
    return RagService().ask(request, user)
