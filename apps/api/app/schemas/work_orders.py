from pydantic import BaseModel, Field


class WorkOrderRead(BaseModel):
    id: str
    asset_id: str
    title: str
    status: str
    priority: str
    assigned_role: str
    description: str | None = None
    audit_events: list[str] = []


class WorkOrderCreate(BaseModel):
    asset_id: str
    title: str = Field(min_length=3, max_length=160)
    priority: str
    recommended_action: str = Field(min_length=3, max_length=2000)


class WorkOrderTransition(BaseModel):
    status: str = Field(pattern="^(draft|review|approved|assigned|closed)$")
    note: str = Field(min_length=3, max_length=500)
