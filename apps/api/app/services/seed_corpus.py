from app.core.security import DEMO_USER
from app.schemas.documents import DocumentIngestRequest
from app.services.document_store import DOCUMENT_STORE


SEED_DOCUMENTS = [
    DocumentIngestRequest(
        title="Spindle vibration SOP",
        document_type="sop",
        source_uri="seed://sop/spindle-vibration",
        content=(
            "Page 1\n"
            "When CNC spindle vibration rises together with torque load and tool wear, stop the active job at the next safe pause. "
            "Inspect tool holder runout, spindle bearing noise, lubrication state, and tool clamping pressure.\n\n"
            "Page 2\n"
            "If vibration remains above the watch threshold after tool replacement, schedule bearing inspection before the next production shift. "
            "Create a high-priority work order and attach torque, vibration, and tool wear readings."
        ),
    ),
    DocumentIngestRequest(
        title="Tool wear escalation SOP",
        document_type="sop",
        source_uri="seed://sop/tool-wear",
        content=(
            "Page 1\n"
            "Rising tool wear with surface finish complaints indicates possible tool holder runout or incorrect feed/speed. "
            "Technicians should compare current wear minutes against expected tool life and inspect tool geometry.\n\n"
            "Page 2\n"
            "Reliability engineers should review historical work orders if the same spindle crosses the high-risk band twice in seven days."
        ),
    ),
    DocumentIngestRequest(
        title="Overheating response SOP",
        document_type="sop",
        source_uri="seed://sop/overheating",
        content=(
            "Page 1\n"
            "If motor temperature rises above safe operating limits, reduce load, inspect cooling airflow, and check lubricant level. "
            "Do not restart until temperature returns to the normal operating range and root cause is documented."
        ),
    ),
    DocumentIngestRequest(
        title="Lockout tagout safety note",
        document_type="safety",
        source_uri="seed://safety/loto",
        content=(
            "Page 1\n"
            "Before spindle housing inspection, isolate electrical and stored mechanical energy. Apply lockout/tagout, verify zero-energy state, "
            "and document the responsible technician before removing guards."
        ),
    ),
    DocumentIngestRequest(
        title="Historical work order: Line 2 spindle",
        document_type="work_order",
        source_uri="seed://work-orders/line-2-spindle-history",
        content=(
            "Page 1\n"
            "Previous Line 2 spindle event showed high torque, vibration, and premature tool wear. Corrective action replaced worn tool holder, "
            "checked bearing preload, and added vibration monitoring during the next shift."
        ),
    ),
]


def ensure_seed_corpus() -> None:
    if DOCUMENT_STORE.chunks:
        return
    for document in SEED_DOCUMENTS:
        DOCUMENT_STORE.ingest(document, DEMO_USER)
