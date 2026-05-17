from fastapi.testclient import TestClient
import pytest

from app.config import Settings
from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "PlantOps Copilot API",
    }


def test_version_endpoint() -> None:
    response = client.get("/version")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "PlantOps Copilot API"
    assert payload["version"] == "0.1.0"
    assert payload["environment"] == "development"
    assert payload["demo_mode"] is True


def test_prometheus_metrics_endpoint() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "plantops_request_count" in response.text


def test_cors_rejects_wildcard_origins() -> None:
    with pytest.raises(ValueError, match="wildcard"):
        Settings(CORS_ORIGINS="*")


def test_production_rejects_demo_mode() -> None:
    settings = Settings(APP_ENV="production", DEMO_MODE=True)

    with pytest.raises(ValueError, match="DEMO_MODE"):
        settings.validate_startup_security()


def test_live_mode_requires_supabase_auth_settings() -> None:
    settings = Settings(DEMO_MODE=False)

    with pytest.raises(ValueError, match="SUPABASE_URL"):
        settings.validate_startup_security()
