from enum import Enum

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.supabase import SupabaseAuthError, SupabaseService, SupabaseUnavailableError


class UserRole(str, Enum):
    technician = "technician"
    reliability_engineer = "reliability_engineer"
    supervisor = "supervisor"
    admin = "admin"


class CurrentUser(BaseModel):
    user_id: str
    email: str
    role: UserRole
    organization_id: str
    plant_id: str
    profile_id: str | None = None
    assigned_plant_ids: list[str] = Field(default_factory=list)


bearer_scheme = HTTPBearer(auto_error=False)


DEMO_USER = CurrentUser(
    user_id="demo-supervisor",
    email="supervisor@demo.local",
    role=UserRole.supervisor,
    organization_id="demo-org",
    plant_id="chennai-plant-a",
    profile_id="demo-profile",
    assigned_plant_ids=["chennai-plant-a"],
)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    if settings.demo_mode and credentials is None:
        return DEMO_USER

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    if settings.demo_mode and token in {"demo", "demo-supervisor"}:
        return DEMO_USER

    # Never trust frontend role claims. Supabase verifies the JWT, then the
    # backend loads role/org/plant from the trusted profiles table.
    service = SupabaseService(settings)
    try:
        verified = service.verify_access_token(token)
        profile = service.load_profile_for_user(verified.user_id)
    except SupabaseAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase bearer token or inactive profile",
        ) from exc
    except SupabaseUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase auth service is unavailable",
        ) from exc

    request.state.auth_token_present = True
    try:
        role = UserRole(profile.role)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile role is not permitted",
        ) from exc

    return CurrentUser(
        user_id=verified.user_id,
        email=profile.email or verified.email or "unknown@example.com",
        role=role,
        organization_id=profile.organization_id,
        plant_id=profile.plant_id,
        profile_id=profile.profile_id,
        assigned_plant_ids=profile.assigned_plant_ids or [profile.plant_id],
    )


def require_roles(*allowed_roles: UserRole):
    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role for this operation",
            )
        return user

    return dependency
