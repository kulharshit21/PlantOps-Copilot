from pydantic import SecretStr
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
import app.core.security as security
import app.api.routes.assets as assets_route
from app.main import app
from app.services.demo_data import DEMO_ASSETS
from app.services.supabase import SupabaseAuthError, SupabaseProfile, VerifiedSupabaseUser


client = TestClient(app)


def live_settings() -> Settings:
    return Settings(
        DEMO_MODE=False,
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_ANON_KEY=SecretStr("anon-placeholder"),
        SUPABASE_SERVICE_ROLE_KEY=SecretStr("service-placeholder"),
    )


class WorkingSupabaseService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def verify_access_token(self, token: str) -> VerifiedSupabaseUser:
        assert token == "valid-token"
        return VerifiedSupabaseUser(user_id="00000000-0000-4000-8000-000000000901", email="asha@example.com")

    def load_profile_for_user(self, user_id: str) -> SupabaseProfile:
        return SupabaseProfile(
            profile_id="00000000-0000-4000-8000-000000000201",
            user_id=user_id,
            organization_id="demo-org",
            plant_id="chennai-plant-a",
            assigned_plant_ids=["chennai-plant-a"],
            role="supervisor",
            display_name="Asha Supervisor",
            email="asha@example.com",
        )


class RejectingSupabaseService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def verify_access_token(self, token: str) -> VerifiedSupabaseUser:
        _ = token
        raise SupabaseAuthError("bad token")

    def load_profile_for_user(self, user_id: str) -> SupabaseProfile:
        raise AssertionError(f"Should not load profile for {user_id}")


class WorkingAssetService(WorkingSupabaseService):
    def list_assets(self, user):
        _ = user
        return DEMO_ASSETS


def test_invalid_token_rejected_when_demo_mode_off(monkeypatch) -> None:
    app.dependency_overrides[get_settings] = live_settings
    monkeypatch.setattr(security, "SupabaseService", RejectingSupabaseService)
    try:
        response = client.get("/assets", headers={"Authorization": "Bearer invalid-token"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert "Invalid Supabase" in response.json()["detail"]


def test_current_user_loads_profile_role_and_scope(monkeypatch) -> None:
    app.dependency_overrides[get_settings] = live_settings
    monkeypatch.setattr(security, "SupabaseService", WorkingSupabaseService)
    monkeypatch.setattr(assets_route, "SupabaseService", WorkingAssetService)
    try:
        response = client.get("/assets", headers={"Authorization": "Bearer valid-token"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["plant_id"] == "chennai-plant-a"


def test_demo_token_only_bypasses_auth_in_demo_mode(monkeypatch) -> None:
    demo_response = client.get("/assets", headers={"Authorization": "Bearer demo"})
    assert demo_response.status_code == 200

    app.dependency_overrides[get_settings] = live_settings
    monkeypatch.setattr(security, "SupabaseService", RejectingSupabaseService)
    try:
        live_response = client.get("/assets", headers={"Authorization": "Bearer demo"})
    finally:
        app.dependency_overrides.clear()

    assert live_response.status_code == 401
