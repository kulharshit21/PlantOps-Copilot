from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


client = TestClient(app)


def test_demo_mode_lists_assets() -> None:
    response = client.get("/assets")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["id"] == "asset-line-2-spindle"
    assert payload[0]["plant_id"] == "chennai-plant-a"


def test_rag_ask_returns_citations() -> None:
    response = client.post(
        "/rag/ask",
        json={"question": "What should next shift do for spindle vibration?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"]
    assert payload["citations"][0]["chunk_id"]
    assert payload["citations"][0]["document_id"]
    assert payload["citations"][0]["source_uri"].startswith("seed://")
    assert payload["recommendation"]
    assert payload["next_steps"]


def test_document_ingest_endpoint_returns_chunks() -> None:
    response = client.post(
        "/documents/ingest",
        json={
            "title": "Demo bearing SOP",
            "document_type": "sop",
            "content": "Page 1\nBearing vibration requires inspection.\n\nPage 2\nUse lockout tagout before opening guards.",
            "source_uri": "seed://test/bearing",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["chunk_count"] >= 1
    assert payload["chunks"][0]["source_uri"] == "seed://test/bearing"


def test_risk_predict_validates_and_scores() -> None:
    response = client.post(
        "/risk/predict",
        json={
            "asset_id": "asset-line-2-spindle",
            "torque_nm": 95,
            "tool_wear_min": 190,
            "vibration_mm_s": 8.5,
            "temperature_c": 72,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert 0 <= payload["risk_score"] <= 1
    assert payload["risk_level"] in {"watch", "high", "critical"}


def test_protected_routes_reject_without_auth_when_demo_mode_off() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(DEMO_MODE=False)
    try:
        response = client.get("/assets")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_supervisor_can_create_demo_work_order() -> None:
    response = client.post(
        "/work-orders",
        json={
            "asset_id": "asset-line-2-spindle",
            "title": "Inspect Line 2 spindle",
            "priority": "high",
            "recommended_action": "Pause job and inspect spindle under LOTO.",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "draft"
