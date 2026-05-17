"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/page-header";
import { apiFetch } from "@/lib/api";
import type { StatusTone } from "@/lib/demo-data";
import { EmptyState, StatusBadge } from "@/lib/status";

type MetricsSummary = {
  request_count: number;
  error_count: number;
  avg_latency_ms: number;
  rag_queries: number;
  risk_predictions: number;
  fallback_count: number;
  status: string;
};

function statusTone(status: string): StatusTone {
  if (status === "healthy") return "healthy";
  if (status === "degraded") return "high";
  if (status === "watch") return "watch";
  return "neutral";
}

export default function ObservabilityPage() {
  const { accessToken } = useAuth();
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function loadMetrics() {
      try {
        const data = await apiFetch<MetricsSummary>("/ops/metrics-summary", { accessToken });
        if (!active) return;
        setMetrics(data);
        setError(null);
      } catch (caught) {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : "Metrics unavailable.");
      }
    }
    void loadMetrics();
    const interval = window.setInterval(() => void loadMetrics(), 10_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [accessToken]);

  const signals: Array<[string, string, StatusTone]> = metrics
    ? [
        ["Requests", metrics.request_count.toString(), statusTone(metrics.status)],
        ["Avg latency", `${metrics.avg_latency_ms} ms`, metrics.avg_latency_ms > 500 ? "watch" : "healthy"],
        ["RAG queries", metrics.rag_queries.toString(), "healthy"],
        ["Fallback count", metrics.fallback_count.toString(), metrics.fallback_count ? "watch" : "healthy"],
        ["Risk predictions", metrics.risk_predictions.toString(), "healthy"],
        ["Errors", metrics.error_count.toString(), metrics.error_count ? "high" : "healthy"],
      ]
    : [];

  return (
    <div>
      <PageHeader
        eyebrow="AIOps"
        title="Operational health"
        description="Live counters for latency, errors, RAG activity, model fallback, and risk predictions."
      />
      {error ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
          Metrics warning: {error}
        </div>
      ) : null}
      {!metrics ? (
        <EmptyState title="Loading metrics" description="Waiting for live API counters." />
      ) : (
        <>
          <div className="mb-4">
            <StatusBadge tone={statusTone(metrics.status)}>Service {metrics.status}</StatusBadge>
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {signals.map(([label, value, tone]) => (
              <article
                key={label}
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
              >
                <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
                <p className="mt-3 text-2xl font-semibold">{value}</p>
                <div className="mt-4">
                  <StatusBadge tone={tone}>Live</StatusBadge>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
