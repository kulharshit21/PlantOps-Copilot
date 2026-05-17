"use client";

import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/page-header";
import { apiFetch } from "@/lib/api";
import { incidents as demoIncidents, type StatusTone } from "@/lib/demo-data";
import { EmptyState, StatusBadge } from "@/lib/status";

type ApiIncident = {
  id: string;
  asset_id: string;
  title: string;
  severity: "low" | "medium" | "high" | "critical" | string;
  status: string;
  reported_at: string;
};

function toneForSeverity(severity: string): StatusTone {
  if (severity === "critical") return "critical";
  if (severity === "high") return "high";
  if (severity === "medium") return "watch";
  return "neutral";
}

export default function IncidentsPage() {
  const { accessToken } = useAuth();
  const [incidents, setIncidents] = useState<ApiIncident[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fallbackIncidents = useMemo<ApiIncident[]>(
    () =>
      demoIncidents.map((incident, index) => ({
        id: `demo-incident-${index}`,
        asset_id: incident.asset,
        title: incident.title,
        severity: incident.severity.toLowerCase(),
        status: "open",
        reported_at: incident.time,
      })),
    [],
  );

  useEffect(() => {
    let active = true;
    async function loadIncidents() {
      setIsLoading(true);
      try {
        const data = await apiFetch<ApiIncident[]>("/incidents", { accessToken });
        if (!active) return;
        setIncidents(data);
        setError(null);
      } catch (exc) {
        if (!active) return;
        setIncidents(fallbackIncidents);
        setError(exc instanceof Error ? exc.message : "API unavailable; showing demo fallback.");
      } finally {
        if (active) setIsLoading(false);
      }
    }

    void loadIncidents();
    return () => {
      active = false;
    };
  }, [accessToken, fallbackIncidents]);

  return (
    <div>
      <PageHeader
        eyebrow="Incident triage"
        title="Open plant incidents"
        description="Operator reports and telemetry anomalies are loaded through backend plant scope."
      />
      {error ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
          Demo fallback active: {error}
        </div>
      ) : null}
      {isLoading ? (
        <EmptyState title="Loading incidents" description="Fetching open incidents for your assigned plant." />
      ) : incidents.length === 0 ? (
        <EmptyState title="No incidents found" description="No active incidents are visible for this plant scope." />
      ) : (
        <div className="grid gap-4">
          {incidents.map((incident) => (
            <article
              key={incident.id}
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold">{incident.title}</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {incident.asset_id} | {incident.reported_at || "time not recorded"}
                  </p>
                </div>
                <StatusBadge tone={toneForSeverity(incident.severity)}>{incident.severity}</StatusBadge>
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">
                Status: {incident.status}. Use the copilot triage flow to retrieve SOP evidence and draft next-shift work.
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
