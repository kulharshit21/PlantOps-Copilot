from app.schemas.ops import MetricsSummary


class OpsService:
    def metrics_summary(self) -> MetricsSummary:
        return MetricsSummary(
            request_count=128,
            error_count=1,
            avg_latency_ms=142.5,
            rag_queries=24,
            risk_predictions=18,
            fallback_count=2,
            status="demo-healthy",
        )
