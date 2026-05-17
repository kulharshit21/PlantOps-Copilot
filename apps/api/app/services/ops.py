from app.schemas.ops import MetricsSummary
from app.services.metrics import METRICS


class OpsService:
    def metrics_summary(self) -> MetricsSummary:
        state = METRICS.snapshot()
        avg_latency = state.total_latency_ms / state.request_count if state.request_count else 0.0
        status = "healthy"
        if state.error_count:
            status = "degraded"
        if state.fallback_count >= 3 or state.no_evidence_responses >= 3:
            status = "watch"
        return MetricsSummary(
            request_count=state.request_count,
            error_count=state.error_count,
            avg_latency_ms=round(avg_latency, 2),
            rag_queries=state.rag_queries,
            risk_predictions=state.risk_predictions,
            fallback_count=state.fallback_count,
            status=status,
        )
