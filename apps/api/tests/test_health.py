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


def test_cors_rejects_wildcard_origins() -> None:
    with pytest.raises(ValueError, match="wildcard"):
        Settings(CORS_ORIGINS="*")
