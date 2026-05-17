from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class MetricsState:
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    rag_queries: int = 0
    no_evidence_responses: int = 0
    risk_predictions: int = 0
    fallback_count: int = 0
    work_order_actions: int = 0
    provider_counts: dict[str, int] = field(default_factory=dict)


class MetricsRegistry:
    def __init__(self) -> None:
        self._state = MetricsState()
        self._lock = Lock()

    def record_request(self, *, latency_ms: float, is_error: bool) -> None:
        with self._lock:
            self._state.request_count += 1
            self._state.total_latency_ms += latency_ms
            if is_error:
                self._state.error_count += 1

    def record_rag(self, *, model_used: str, fallback_used: bool, no_evidence: bool) -> None:
        with self._lock:
            self._state.rag_queries += 1
            if fallback_used:
                self._state.fallback_count += 1
            if no_evidence:
                self._state.no_evidence_responses += 1
            self._state.provider_counts[model_used] = self._state.provider_counts.get(model_used, 0) + 1

    def record_risk_prediction(self) -> None:
        with self._lock:
            self._state.risk_predictions += 1

    def record_work_order_action(self) -> None:
        with self._lock:
            self._state.work_order_actions += 1

    def snapshot(self) -> MetricsState:
        with self._lock:
            return MetricsState(
                request_count=self._state.request_count,
                error_count=self._state.error_count,
                total_latency_ms=self._state.total_latency_ms,
                rag_queries=self._state.rag_queries,
                no_evidence_responses=self._state.no_evidence_responses,
                risk_predictions=self._state.risk_predictions,
                fallback_count=self._state.fallback_count,
                work_order_actions=self._state.work_order_actions,
                provider_counts=dict(self._state.provider_counts),
            )

    def prometheus_text(self) -> str:
        state = self.snapshot()
        avg_latency = state.total_latency_ms / state.request_count if state.request_count else 0.0
        lines = [
            "# HELP plantops_request_count Total HTTP requests observed by the API.",
            "# TYPE plantops_request_count counter",
            f"plantops_request_count {state.request_count}",
            "# HELP plantops_error_count Total HTTP error responses.",
            "# TYPE plantops_error_count counter",
            f"plantops_error_count {state.error_count}",
            "# HELP plantops_avg_latency_ms Average HTTP request latency in milliseconds.",
            "# TYPE plantops_avg_latency_ms gauge",
            f"plantops_avg_latency_ms {avg_latency:.3f}",
            "# HELP plantops_rag_queries Total RAG requests.",
            "# TYPE plantops_rag_queries counter",
            f"plantops_rag_queries {state.rag_queries}",
            "# HELP plantops_no_evidence_responses Total RAG no-evidence responses.",
            "# TYPE plantops_no_evidence_responses counter",
            f"plantops_no_evidence_responses {state.no_evidence_responses}",
            "# HELP plantops_fallback_count Total provider fallback responses.",
            "# TYPE plantops_fallback_count counter",
            f"plantops_fallback_count {state.fallback_count}",
            "# HELP plantops_risk_predictions Total risk predictions.",
            "# TYPE plantops_risk_predictions counter",
            f"plantops_risk_predictions {state.risk_predictions}",
            "# HELP plantops_work_order_actions Total work-order write actions.",
            "# TYPE plantops_work_order_actions counter",
            f"plantops_work_order_actions {state.work_order_actions}",
        ]
        for provider, count in sorted(state.provider_counts.items()):
            safe_provider = provider.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'plantops_llm_provider_used{{provider="{safe_provider}"}} {count}')
        return "\n".join(lines) + "\n"


METRICS = MetricsRegistry()
