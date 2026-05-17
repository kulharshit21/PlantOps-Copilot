from enum import Enum

from pydantic import BaseModel


class AssetStatus(str, Enum):
    healthy = "healthy"
    watch = "watch"
    high_risk = "high_risk"
    critical = "critical"


class AssetRead(BaseModel):
    id: str
    name: str
    line: str
    status: AssetStatus
    risk_score: float
    plant_id: str
