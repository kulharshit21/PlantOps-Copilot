from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, UserRole, require_roles
from app.schemas.ops import MetricsSummary, SupabaseHealthRead
from app.services.ops import OpsService
from app.services.supabase_client import SupabaseClient

router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/metrics-summary", response_model=MetricsSummary)
def metrics_summary(
    user: CurrentUser = Depends(require_roles(UserRole.supervisor, UserRole.admin)),
) -> MetricsSummary:
    _ = user
    return OpsService().metrics_summary()


@router.get("/supabase-health", response_model=SupabaseHealthRead)
def supabase_health(
    user: CurrentUser = Depends(require_roles(UserRole.supervisor, UserRole.admin)),
) -> SupabaseHealthRead:
    _ = user
    health = SupabaseClient().health()
    return SupabaseHealthRead(
        configured=health.configured,
        reachable=health.reachable,
        project_url=health.project_url,
        detail=health.detail,
    )
