from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.incidents import IncidentRead
from app.services.demo_data import DEMO_INCIDENTS

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentRead])
def list_incidents(user: CurrentUser = Depends(get_current_user)) -> list[IncidentRead]:
    _ = user
    return DEMO_INCIDENTS
