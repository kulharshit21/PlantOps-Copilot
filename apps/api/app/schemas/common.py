from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    detail: str
    request_id: str | None = None


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    service: str = Field(examples=["PlantOps Copilot API"])


class VersionResponse(BaseModel):
    service: str
    version: str
    environment: str
    demo_mode: bool


class Citation(BaseModel):
    chunk_id: str
    title: str
    source_uri: str
    source_page: int | None = None
