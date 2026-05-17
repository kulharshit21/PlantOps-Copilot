from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, get_current_user
from app.schemas.incidents import IncidentRead
from app.services.demo_data import DEMO_INCIDENTS
from app.services.supabase import SupabaseService, SupabaseServiceError

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> list[IncidentRead]:
    try:
        return SupabaseService(settings).list_incidents(user)
    except SupabaseServiceError as exc:
        if settings.demo_mode:
            return DEMO_INCIDENTS
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase incidents data is unavailable",
        ) from exc
