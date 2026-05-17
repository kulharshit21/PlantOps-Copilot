from pydantic import BaseModel, Field


class WorkOrderRead(BaseModel):
    id: str
    asset_id: str
    title: str
    status: str
    priority: str
    assigned_role: str


class WorkOrderCreate(BaseModel):
    asset_id: str
    title: str = Field(min_length=3, max_length=160)
    priority: str
    recommended_action: str = Field(min_length=3, max_length=2000)
