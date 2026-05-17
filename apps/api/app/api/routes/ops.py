from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, UserRole, require_roles
from app.schemas.ops import MetricsSummary
from app.services.ops import OpsService

router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/metrics-summary", response_model=MetricsSummary)
def metrics_summary(
    user: CurrentUser = Depends(require_roles(UserRole.supervisor, UserRole.admin)),
) -> MetricsSummary:
    _ = user
    return OpsService().metrics_summary()
