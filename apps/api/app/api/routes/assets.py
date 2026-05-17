from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import CurrentUser, get_current_user
from app.schemas.assets import AssetRead
from app.services.demo_data import DEMO_ASSETS
from app.services.supabase import SupabaseService, SupabaseServiceError

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetRead])
def list_assets(
    user: CurrentUser = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
) -> list[AssetRead]:
    try:
        return SupabaseService(settings).list_assets(user)
    except SupabaseServiceError as exc:
        if settings.demo_mode:
            return [asset for asset in DEMO_ASSETS if asset.plant_id == user.plant_id]
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase assets data is unavailable",
        ) from exc
