from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_work_order_lifecycle_transition() -> None:
    created = client.post(
        "/work-orders",
        json={
            "asset_id": "asset-line-2-spindle",
            "title": "Inspect spindle",
            "priority": "high",
            "recommended_action": "Inspect cited vibration issue.",
        },
    )
    assert created.status_code == 200
    order_id = created.json()["id"]

    approved = client.patch(
        f"/work-orders/{order_id}",
        json={"status": "approved", "note": "Supervisor approved for next shift."},
    )

    assert approved.status_code == 200
    payload = approved.json()
    assert payload["status"] == "approved"
    assert payload["audit_events"]
