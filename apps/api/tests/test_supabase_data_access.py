from typing import Any

from pydantic import SecretStr

from app.core.config import Settings
from app.core.security import CurrentUser, UserRole
from app.services.supabase import SupabaseAuthError, SupabaseService


class RecordingSupabaseService(SupabaseService):
    def __init__(self) -> None:
        super().__init__(
            Settings(
                SUPABASE_URL="https://example.supabase.co",
                SUPABASE_ANON_KEY=SecretStr("anon-placeholder"),
                SUPABASE_SERVICE_ROLE_KEY=SecretStr("service-placeholder"),
            )
        )
        self.calls: list[tuple[str, str, Any]] = []

    def _request_json(self, method: str, path: str, **kwargs) -> Any:
        self.calls.append((method, path, kwargs))
        if path == "/rest/v1/assets":
            return [
                {
                    "id": "asset-1",
                    "name": "Line 2 CNC Spindle",
                    "line_name": "Line 2",
                    "status": "degraded",
                    "risk_score": 0.74,
                    "plant_id": "plant-a",
                }
            ]
        if path == "/rest/v1/rag_queries":
            return [{"id": "rag-1"}]
        return []


def scoped_user() -> CurrentUser:
    return CurrentUser(
        user_id="user-a",
        email="user@example.com",
        role=UserRole.supervisor,
        organization_id="org-a",
        plant_id="plant-a",
        profile_id="profile-a",
        assigned_plant_ids=["plant-a"],
    )


def test_list_assets_applies_org_and_plant_filters() -> None:
    service = RecordingSupabaseService()

    assets = service.list_assets(scoped_user())

    assert assets[0].status == "high_risk"
    method, path, kwargs = service.calls[0]
    assert method == "GET"
    assert path == "/rest/v1/assets"
    assert kwargs["query"]["organization_id"] == "eq.org-a"
    assert kwargs["query"]["plant_id"] == "eq.plant-a"


def test_wrong_plant_scope_is_rejected_before_query() -> None:
    service = RecordingSupabaseService()

    try:
        service.list_document_chunks(scoped_user(), plant_id="plant-b")
    except SupabaseAuthError:
        pass
    else:
        raise AssertionError("Expected wrong plant scope to be rejected")

    assert service.calls == []


def test_create_rag_query_uses_server_side_scope() -> None:
    service = RecordingSupabaseService()

    service.create_rag_query(
        scoped_user(),
        query="What happened?",
        answer="Use cited evidence.",
        citations=[{"chunk_id": "chunk-1"}],
        model_used="mock",
        fallback_used=False,
        latency_ms=42,
    )

    _, path, kwargs = service.calls[0]
    assert path == "/rest/v1/rag_queries"
    assert kwargs["payload"]["organization_id"] == "org-a"
    assert kwargs["payload"]["plant_id"] == "plant-a"
    assert kwargs["payload"]["created_by"] == "profile-a"
