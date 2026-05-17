from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.triage import TriageRunRequest, TriageRunResponse
from app.services.audit import AuditLogService
from app.services.triage import TriageWorkflow

router = APIRouter(prefix="/triage", tags=["triage"])


@router.post("/run", response_model=TriageRunResponse)
def run_triage(
    request: TriageRunRequest,
    user: CurrentUser = Depends(get_current_user),
) -> TriageRunResponse:
    response = TriageWorkflow().run(request, user)
    AuditLogService().record(
        actor_id=user.user_id,
        action="triage.run",
        resource_type="asset",
        resource_id=request.asset_id,
        metadata={"risk_score": response.risk_score, "urgency": response.urgency},
    )
    return response
