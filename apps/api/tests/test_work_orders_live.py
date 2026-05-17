from fastapi.testclient import TestClient

import app.api.routes.work_orders as work_orders_route
from app.main import app
from app.schemas.work_orders import WorkOrderRead


client = TestClient(app)


class RecordingWorkOrderService:
    audit_logs: list[dict] = []

    def __init__(self, settings) -> None:
        self.settings = settings

    def list_work_orders(self, user):
        _ = user
        return []

    def create_work_order(self, user, *, asset_id, title, description, priority, ai_recommendation):
        _ = user
        _ = ai_recommendation
        return WorkOrderRead(
            id="wo-live-1",
            asset_id=asset_id,
            title=title,
            status="draft",
            priority=priority,
            assigned_role="reliability_engineer",
            description=description,
            audit_events=[],
        )

    def update_work_order(self, user, *, order_id, status, note):
        _ = user
        _ = note
        return WorkOrderRead(
            id=order_id,
            asset_id="asset-line-2-spindle",
            title="Inspect spindle",
            status=status,
            priority="high",
            assigned_role="reliability_engineer",
            description="Updated live order",
            audit_events=[f"status:{status}"],
        )

    def create_audit_log(self, user, **kwargs):
        self.audit_logs.append({"user": user.user_id, **kwargs})


def test_live_work_order_create_and_transition_persist_audit(monkeypatch) -> None:
    RecordingWorkOrderService.audit_logs = []
    monkeypatch.setattr(work_orders_route, "SupabaseService", RecordingWorkOrderService)

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
    assert created.json()["id"] == "wo-live-1"

    approved = client.patch(
        "/work-orders/wo-live-1",
        json={"status": "approved", "note": "Supervisor approved."},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert [entry["action"] for entry in RecordingWorkOrderService.audit_logs] == [
        "work_order.create_draft",
        "work_order.approved",
    ]
