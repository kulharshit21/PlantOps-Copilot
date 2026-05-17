from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_triage_run_returns_structured_work_order() -> None:
    response = client.post(
        "/triage/run",
        json={
            "question": "Line 2 spindle torque is high and vibration is rising. What should next shift do?",
            "asset_id": "asset-line-2-spindle",
            "telemetry": {
                "torque_nm": 104,
                "tool_wear_min": 220,
                "vibration_mm_s": 9.4,
                "temperature_c": 78,
            },
            "incident_notes": "Operator reported vibration.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_score"] > 0
    assert payload["drafted_work_order"]["title"]
    assert payload["citations"]
    assert payload["safety_checks"]
