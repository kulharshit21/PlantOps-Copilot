from pydantic import BaseModel, Field

from app.schemas.documents import RetrievedChunk


class TriageTelemetry(BaseModel):
    torque_nm: float = Field(ge=0)
    tool_wear_min: float = Field(ge=0)
    vibration_mm_s: float = Field(ge=0)
    temperature_c: float = Field(ge=-50, le=250)


class TriageRunRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    asset_id: str
    telemetry: TriageTelemetry
    incident_notes: str | None = Field(default=None, max_length=2000)
    create_draft_work_order: bool = False


class DraftedWorkOrder(BaseModel):
    title: str
    priority: str
    description: str
    acceptance_criteria: list[str]


class TriageRunResponse(BaseModel):
    issue_summary: str
    urgency: str
    risk_score: float
    likely_failure_mode: str
    recommended_actions: list[str]
    safety_checks: list[str]
    parts_tools_needed: list[str]
    drafted_work_order: DraftedWorkOrder
    citations: list[RetrievedChunk]
    model_used: str
    created_work_order_id: str | None = None
