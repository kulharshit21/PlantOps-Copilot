from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.security import UserRole, require_roles
from app.schemas.security import SecurityReadinessResponse
from app.services.readiness import ReadinessService

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/readiness", response_model=SecurityReadinessResponse)
def security_readiness(
    _user=Depends(require_roles(UserRole.supervisor, UserRole.admin)),
    settings: Settings = Depends(get_settings),
) -> SecurityReadinessResponse:
    return ReadinessService(settings).security_readiness()
