"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/page-header";
import { apiFetch } from "@/lib/api";
import {
  assets as demoAssets,
  incidents as demoIncidents,
  quickActions,
  workOrders as demoWorkOrders,
  type StatusTone,
} from "@/lib/demo-data";
import { EmptyState, StatusBadge } from "@/lib/status";

type ApiAsset = {
  id: string;
  name: string;
  line: string;
  status: "healthy" | "watch" | "high_risk" | "critical";
  risk_score: number;
  plant_id: string;
};

type ApiIncident = {
  id: string;
  asset_id: string;
  title: string;
  severity: string;
  status: string;
  reported_at: string;
};

type WorkOrder = {
  id: string;
  asset_id: string;
  title: string;
  status: string;
  priority: string;
  assigned_role: string;
  description: string | null;
  audit_events: string[];
};

type MetricsSummary = {
  request_count: number;
  error_count: number;
  avg_latency_ms: number;
  rag_queries: number;
  risk_predictions: number;
  fallback_count: number;
  status: string;
};

function toneForAsset(asset: ApiAsset): StatusTone {
  if (asset.status === "healthy") return "healthy";
  if (asset.status === "watch") return "watch";
  if (asset.status === "high_risk") return "high";
  return "critical";
}

function toneForSeverity(severity: string): StatusTone {
  if (severity === "critical") return "critical";
  if (severity === "high") return "high";
  if (severity === "medium") return "watch";
  return "neutral";
}

export default function DashboardPage() {
  const { accessToken } = useAuth();
  const [assets, setAssets] = useState<ApiAsset[]>([]);
  const [incidents, setIncidents] = useState<ApiIncident[]>([]);
  const [orders, setOrders] = useState<WorkOrder[]>([]);
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fallbacks = useMemo(
    () => ({
      assets: demoAssets.map((asset) => ({
        id: asset.id,
        name: asset.name,
        line: asset.line,
        status: asset.tone === "critical" ? "critical" : asset.tone === "high" ? "high_risk" : "watch",
        risk_score: asset.risk / 100,
        plant_id: "chennai-plant-a",
      })) as ApiAsset[],
      incidents: demoIncidents.map((incident, index) => ({
        id: `demo-incident-${index}`,
        asset_id: incident.asset,
        title: incident.title,
        severity: incident.severity.toLowerCase(),
        status: "open",
        reported_at: incident.time,
      })),
      orders: demoWorkOrders.map((order, index) => ({
        id: `demo-wo-${index}`,
        asset_id: order.asset,
        title: order.title,
        status: order.status.toLowerCase(),
        priority: order.priority.toLowerCase(),
        assigned_role: "reliability_engineer",
        description: `Due ${order.due}`,
        audit_events: ["demo:fallback"],
      })),
    }),
    [],
  );

  useEffect(() => {
    let active = true;
    async function loadDashboard() {
      setIsLoading(true);
      try {
        const [assetData, incidentData, orderData, metricData] = await Promise.all([
          apiFetch<ApiAsset[]>("/assets", { accessToken }),
          apiFetch<ApiIncident[]>("/incidents", { accessToken }),
          apiFetch<WorkOrder[]>("/work-orders", { accessToken }),
          apiFetch<MetricsSummary>("/ops/metrics-summary", { accessToken }),
        ]);
        if (!active) return;
        setAssets(assetData);
        setIncidents(incidentData);
        setOrders(orderData);
        setMetrics(metricData);
        setError(null);
      } catch (caught) {
        if (!active) return;
        setAssets(fallbacks.assets);
        setIncidents(fallbacks.incidents);
        setOrders(fallbacks.orders);
        setMetrics(null);
        setError(caught instanceof Error ? caught.message : "Backend unavailable; showing demo fallback.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadDashboard();
    return () => {
      active = false;
    };
  }, [accessToken, fallbacks]);

  const criticalAssets = assets.filter((asset) => asset.status === "critical" || asset.status === "high_risk");
  const healthyCount = assets.filter((asset) => asset.status === "healthy").length;
  const watchCount = assets.filter((asset) => asset.status === "watch").length;

  return (
    <div>
      <PageHeader
        eyebrow="Supervisor overview"
        title="Plant health dashboard"
        description="Shift-ready live view of asset risk, active incidents, AI work-order drafts, and system trust signals."
        action={
          <Link
            href="/copilot"
            className="inline-flex h-11 items-center justify-center rounded-md bg-teal-600 px-4 text-sm font-semibold text-white hover:bg-teal-700"
          >
            Ask copilot about Line 2
          </Link>
        }
      />

      {error ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
          Demo fallback active: {error}
        </div>
      ) : null}

      {isLoading ? (
        <EmptyState title="Loading dashboard" description="Fetching live plant context from the backend." />
      ) : (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              ["Total assets", assets.length.toString(), "Across assigned plant"],
              ["High-risk assets", criticalAssets.length.toString(), "Immediate review"],
              ["Watch assets", watchCount.toString(), "Monitor next shift"],
              ["Healthy assets", healthyCount.toString(), "Normal operation"],
            ].map(([label, value, caption]) => (
              <article
                key={label}
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
              >
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
                <p className="mt-3 text-3xl font-semibold">{value}</p>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{caption}</p>
              </article>
            ))}
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">High-risk assets</h2>
                <StatusBadge tone={criticalAssets.length ? "critical" : "healthy"}>
                  {criticalAssets.length ? "Review" : "Stable"}
                </StatusBadge>
              </div>
              <div className="space-y-3">
                {assets.map((asset) => (
                  <div
                    key={asset.id}
                    className="grid gap-4 rounded-lg border border-slate-200 bg-slate-50 p-4 md:grid-cols-[1fr_auto] dark:border-slate-800 dark:bg-slate-950"
                  >
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold">{asset.name}</p>
                        <StatusBadge tone={toneForAsset(asset)}>{asset.status.replace("_", " ")}</StatusBadge>
                      </div>
                      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                        {asset.id} | {asset.line} | Plant {asset.plant_id}
                      </p>
                    </div>
                    <div className="min-w-32 text-right">
                      <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Risk</p>
                      <p className="text-2xl font-semibold">{Math.round(asset.risk_score * 100)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h2 className="text-lg font-semibold">System status</h2>
              <div className="mt-4 space-y-3">
                {[
                  ["Requests", metrics?.request_count.toString() ?? "fallback"],
                  ["RAG queries", metrics?.rag_queries.toString() ?? "fallback"],
                  ["Fallbacks", metrics?.fallback_count.toString() ?? "fallback"],
                  ["Errors", metrics?.error_count.toString() ?? "fallback"],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3 dark:bg-slate-950">
                    <p className="text-sm font-medium">{label}</p>
                    <StatusBadge tone={value === "0" || value === "fallback" ? "healthy" : "watch"}>{value}</StatusBadge>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-2">
            <Panel title="Recent incidents">
              {incidents.map((incident) => (
                <div key={incident.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-950">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium">{incident.title}</p>
                    <StatusBadge tone={toneForSeverity(incident.severity)}>{incident.severity}</StatusBadge>
                  </div>
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    {incident.asset_id} | {incident.reported_at}
                  </p>
                </div>
              ))}
            </Panel>

            <Panel title="Pending work orders">
              {orders.map((order) => (
                <div key={order.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-950">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium">{order.title}</p>
                    <StatusBadge tone={order.priority === "urgent" ? "critical" : "watch"}>
                      {order.priority}
                    </StatusBadge>
                  </div>
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    {order.asset_id} | {order.status}
                  </p>
                </div>
              ))}
            </Panel>
          </section>

          <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Link
                  key={action.title}
                  href={action.href}
                  className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-teal-300 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-teal-800"
                >
                  <Icon className="text-teal-600 dark:text-teal-300" aria-hidden="true" />
                  <p className="mt-4 font-semibold">{action.title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
                    {action.description}
                  </p>
                </Link>
              );
            })}
          </section>
        </>
      )}
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="mt-4 space-y-3">{children}</div>
    </div>
  );
}
