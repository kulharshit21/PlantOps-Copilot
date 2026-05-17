from pydantic import BaseModel


class IncidentRead(BaseModel):
    id: str
    asset_id: str
    title: str
    severity: str
    status: str
    reported_at: str
