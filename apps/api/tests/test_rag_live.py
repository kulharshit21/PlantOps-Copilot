from fastapi.testclient import TestClient

import app.services.rag as rag_service
from app.main import app
from app.schemas.documents import RetrievedChunk


client = TestClient(app)


class RecordingRagSupabaseService:
    rag_queries: list[dict] = []
    audit_logs: list[dict] = []

    def __init__(self, settings) -> None:
        self.settings = settings

    def match_document_chunks(self, user, *, query_embedding, plant_id, top_k):
        assert user.organization_id == "demo-org"
        assert len(query_embedding) == 768
        assert top_k == 4
        return [
            RetrievedChunk(
                chunk_id="chunk-live-rag",
                document_id="doc-live-rag",
                title="Live SOP",
                content="Spindle vibration with high torque requires lockout tagout and inspection.",
                source_uri="supabase://chunk-live-rag",
                source_page=2,
                score=0.88,
            )
        ]

    def create_rag_query(self, user, **kwargs):
        self.rag_queries.append({"user": user.user_id, **kwargs})

    def create_audit_log(self, user, **kwargs):
        self.audit_logs.append({"user": user.user_id, **kwargs})


def test_rag_ask_persists_query_and_audit(monkeypatch) -> None:
    RecordingRagSupabaseService.rag_queries = []
    RecordingRagSupabaseService.audit_logs = []
    monkeypatch.setattr(rag_service, "SupabaseService", RecordingRagSupabaseService)

    response = client.post(
        "/rag/ask",
        json={"question": "What should next shift do for high spindle vibration?", "top_k": 4},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"][0]["chunk_id"] == "chunk-live-rag"
    assert RecordingRagSupabaseService.rag_queries[0]["citations"][0]["chunk_id"] == "chunk-live-rag"
    assert RecordingRagSupabaseService.audit_logs[0]["action"] == "rag.ask"
