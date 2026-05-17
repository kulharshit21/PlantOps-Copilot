from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.schemas.assets import AssetRead
from app.services.demo_data import DEMO_ASSETS

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetRead])
def list_assets(user: CurrentUser = Depends(get_current_user)) -> list[AssetRead]:
    return [asset for asset in DEMO_ASSETS if asset.plant_id == user.plant_id]
