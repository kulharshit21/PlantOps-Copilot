from pydantic import BaseModel


class MetricsSummary(BaseModel):
    request_count: int
    error_count: int
    avg_latency_ms: float
    rag_queries: int
    risk_predictions: int
    fallback_count: int
    status: str


class SupabaseHealthRead(BaseModel):
    configured: bool
    reachable: bool
    project_url: str | None
    detail: str
