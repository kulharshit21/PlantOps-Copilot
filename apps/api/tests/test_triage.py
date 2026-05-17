from fastapi.testclient import TestClient

import app.services.rag as rag_service
import app.services.triage as triage_service
from app.main import app
from app.schemas.assets import AssetRead, AssetStatus
from app.schemas.documents import RetrievedChunk
from app.schemas.work_orders import WorkOrderRead


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


class RecordingTriageSupabaseService:
    model_predictions: list[dict] = []
    audit_logs: list[dict] = []
    work_orders: list[dict] = []

    def __init__(self, settings) -> None:
        self.settings = settings

    def match_document_chunks(self, user, *, query_embedding, plant_id, top_k):
        _ = user
        _ = query_embedding
        _ = plant_id
        _ = top_k
        return [
            RetrievedChunk(
                chunk_id="chunk-triage",
                document_id="doc-triage",
                title="Spindle SOP",
                content="High torque with vibration requires lockout tagout and spindle inspection.",
                source_uri="supabase://chunk-triage",
                source_page=1,
                score=0.9,
            )
        ]

    def create_rag_query(self, user, **kwargs):
        _ = user
        _ = kwargs

    def get_asset(self, user, asset_id):
        _ = user
        return AssetRead(
            id=asset_id,
            name="Line 2 CNC Spindle",
            line="Line 2",
            status=AssetStatus.high_risk,
            risk_score=0.86,
            plant_id="chennai-plant-a",
        )

    def create_model_prediction(self, user, **kwargs):
        self.model_predictions.append({"user": user.user_id, **kwargs})

    def create_work_order(self, user, **kwargs):
        self.work_orders.append({"user": user.user_id, **kwargs})
        return WorkOrderRead(
            id="wo-triage-live",
            asset_id=kwargs["asset_id"],
            title=kwargs["title"],
            status="draft",
            priority=kwargs["priority"],
            assigned_role="reliability_engineer",
            description=kwargs["description"],
            audit_events=[],
        )

    def create_audit_log(self, user, **kwargs):
        self.audit_logs.append({"user": user.user_id, **kwargs})


def test_triage_persists_prediction_audit_and_optional_draft(monkeypatch) -> None:
    RecordingTriageSupabaseService.model_predictions = []
    RecordingTriageSupabaseService.audit_logs = []
    RecordingTriageSupabaseService.work_orders = []
    monkeypatch.setattr(triage_service, "SupabaseService", RecordingTriageSupabaseService)
    monkeypatch.setattr(rag_service, "SupabaseService", RecordingTriageSupabaseService)

    response = client.post(
        "/triage/run",
        json={
            "question": "Line 2 spindle torque is high and vibration is rising. What should next shift do?",
            "asset_id": "asset-line-2-spindle",
            "create_draft_work_order": True,
            "telemetry": {
                "torque_nm": 104,
                "tool_wear_min": 220,
                "vibration_mm_s": 9.4,
                "temperature_c": 78,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["created_work_order_id"] == "wo-triage-live"
    assert RecordingTriageSupabaseService.model_predictions
    assert RecordingTriageSupabaseService.work_orders
    assert any(entry["action"] == "triage.run" for entry in RecordingTriageSupabaseService.audit_logs)
