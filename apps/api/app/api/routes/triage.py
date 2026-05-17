from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, get_current_user
from app.schemas.triage import TriageRunRequest, TriageRunResponse
from app.services.triage import TriageWorkflow

router = APIRouter(prefix="/triage", tags=["triage"])


@router.post("/run", response_model=TriageRunResponse)
def run_triage(
    request: TriageRunRequest,
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> TriageRunResponse:
    return TriageWorkflow(settings).run(request, user)
