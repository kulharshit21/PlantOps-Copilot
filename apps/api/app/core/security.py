from enum import Enum

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import Settings, get_settings


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


bearer_scheme = HTTPBearer(auto_error=False)


DEMO_USER = CurrentUser(
    user_id="demo-supervisor",
    email="supervisor@demo.local",
    role=UserRole.supervisor,
    organization_id="demo-org",
    plant_id="chennai-plant-a",
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

    # Supabase JWT verification will be implemented with project JWKS/secret.
    # Never trust frontend role claims without backend verification.
    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    request.state.auth_token_present = True
    return CurrentUser(
        user_id="verified-placeholder",
        email="verified-user@example.com",
        role=UserRole.technician,
        organization_id="demo-org",
        plant_id="chennai-plant-a",
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
