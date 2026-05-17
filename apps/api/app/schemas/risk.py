from pydantic import BaseModel, Field


class RiskPredictRequest(BaseModel):
    asset_id: str
    torque_nm: float = Field(ge=0)
    tool_wear_min: float = Field(ge=0)
    vibration_mm_s: float = Field(ge=0)
    temperature_c: float = Field(ge=-50, le=250)


class RiskPredictResponse(BaseModel):
    risk_score: float = Field(ge=0, le=1)
    risk_level: str
    likely_failure_modes: list[str]
    top_features: list[str]
    model_version: str
    warning: str | None = None
