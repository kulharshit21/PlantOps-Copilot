from app.schemas.assets import AssetRead, AssetStatus
from app.schemas.documents import DocumentRead, RetrievedChunk
from app.schemas.incidents import IncidentRead
from app.schemas.work_orders import WorkOrderRead


DEMO_ASSETS = [
    AssetRead(
        id="asset-line-2-spindle",
        name="Line 2 CNC Spindle",
        line="Line 2",
        status=AssetStatus.high_risk,
        risk_score=0.86,
        plant_id="chennai-plant-a",
    ),
    AssetRead(
        id="asset-compressor-1",
        name="Air Compressor 1",
        line="Utilities",
        status=AssetStatus.watch,
        risk_score=0.42,
        plant_id="chennai-plant-a",
    ),
]

DEMO_INCIDENTS = [
    IncidentRead(
        id="incident-spindle-vibration",
        asset_id="asset-line-2-spindle",
        title="High torque, rising tool wear, vibration reported",
        severity="high",
        status="open",
        reported_at="2026-05-17T15:30:00Z",
    )
]

DEMO_DOCUMENTS = [
    DocumentRead(
        id="doc-spindle-sop",
        title="Spindle vibration SOP",
        document_type="sop",
        plant_id="chennai-plant-a",
    )
]

DEMO_CHUNKS = [
    RetrievedChunk(
        chunk_id="chunk-spindle-vibration-001",
        title="Spindle vibration SOP",
        content="If vibration rises with torque and tool wear, pause the job, inspect tool holder runout, verify lubrication, and schedule bearing inspection.",
        source_uri="sop://spindle-vibration",
        source_page=1,
    ),
    RetrievedChunk(
        chunk_id="chunk-lockout-001",
        title="Lockout safety note",
        content="Before spindle housing inspection, isolate energy, apply lockout/tagout, and verify zero-energy state.",
        source_uri="sop://lockout-tagout",
        source_page=1,
    ),
]

DEMO_WORK_ORDERS = [
    WorkOrderRead(
        id="wo-spindle-inspection",
        asset_id="asset-line-2-spindle",
        title="Inspect Line 2 spindle vibration",
        status="draft",
        priority="high",
        assigned_role="reliability_engineer",
    )
]
