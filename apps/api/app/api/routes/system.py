from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.common import HealthResponse, VersionResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/version", response_model=VersionResponse)
def version(settings: Settings = Depends(get_settings)) -> VersionResponse:
    return VersionResponse(
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        demo_mode=settings.demo_mode,
    )
