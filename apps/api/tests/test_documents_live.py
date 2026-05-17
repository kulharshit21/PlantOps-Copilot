from fastapi.testclient import TestClient

import app.api.routes.documents as documents_route
from app.main import app
from app.schemas.documents import DocumentRead, RetrievedChunk


client = TestClient(app)


class RecordingDocumentService:
    created_documents: list[dict] = []
    created_chunks: list[dict] = []
    audit_logs: list[dict] = []

    def __init__(self, settings) -> None:
        self.settings = settings

    def create_document(self, user, *, title, document_type, source_uri, plant_id):
        self.created_documents.append(
            {
                "organization_id": user.organization_id,
                "plant_id": plant_id,
                "title": title,
                "document_type": document_type,
            }
        )
        return DocumentRead(
            id="doc-live-1",
            title=title,
            document_type=document_type,
            plant_id=plant_id,
            source_uri=source_uri,
        )

    def create_document_chunks(self, user, *, document_id, title, chunks, plant_id):
        _ = user
        self.created_chunks.extend(chunks)
        return [
            RetrievedChunk(
                chunk_id="chunk-live-1",
                document_id=document_id,
                title=title,
                content=chunks[0]["content"],
                source_uri=chunks[0]["source_uri"],
                source_page=chunks[0]["source_page"],
                score=None,
            )
        ]

    def create_audit_log(self, user, *, action, entity_type, entity_id, details, plant_id):
        self.audit_logs.append(
            {
                "actor": user.user_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "details": details,
                "plant_id": plant_id,
            }
        )


def test_document_ingest_persists_chunks_and_audit(monkeypatch) -> None:
    RecordingDocumentService.created_documents = []
    RecordingDocumentService.created_chunks = []
    RecordingDocumentService.audit_logs = []
    monkeypatch.setattr(documents_route, "SupabaseService", RecordingDocumentService)

    response = client.post(
        "/documents/ingest",
        json={
            "title": "Live spindle SOP",
            "document_type": "sop",
            "content": "Page 1\nSpindle vibration with torque requires inspection and lockout tagout before work.",
            "source_uri": "seed://live-spindle",
        },
    )

    assert response.status_code == 200
    assert RecordingDocumentService.created_documents[0]["organization_id"] == "demo-org"
    assert RecordingDocumentService.created_chunks[0]["embedding"]
    assert len(RecordingDocumentService.created_chunks[0]["embedding"]) == 768
    assert RecordingDocumentService.audit_logs[0]["action"] == "document.ingest"
