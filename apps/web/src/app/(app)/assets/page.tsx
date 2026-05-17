"use client";

import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/page-header";
import { apiFetch } from "@/lib/api";
import { assets as demoAssets, type StatusTone } from "@/lib/demo-data";
import { EmptyState, StatusBadge } from "@/lib/status";

type ApiAsset = {
  id: string;
  name: string;
  line: string;
  status: "healthy" | "watch" | "high_risk" | "critical";
  risk_score: number;
  plant_id: string;
};

function toneForStatus(status: ApiAsset["status"]): StatusTone {
  if (status === "healthy") return "healthy";
  if (status === "watch") return "watch";
  if (status === "high_risk") return "high";
  return "critical";
}

function labelForStatus(status: ApiAsset["status"]) {
  return status.replace("_", " ");
}

export default function AssetsPage() {
  const { accessToken } = useAuth();
  const [assets, setAssets] = useState<ApiAsset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fallbackAssets = useMemo<ApiAsset[]>(
    () =>
      demoAssets.map((asset) => ({
        id: asset.id,
        name: asset.name,
        line: asset.line,
        status: asset.status === "Critical" ? "critical" : asset.tone === "high" ? "high_risk" : "watch",
        risk_score: asset.risk / 100,
        plant_id: "chennai-plant-a",
      })),
    [],
  );

  useEffect(() => {
    let active = true;
    async function loadAssets() {
      setIsLoading(true);
      try {
        const data = await apiFetch<ApiAsset[]>("/assets", { accessToken });
        if (!active) return;
        setAssets(data);
        setError(null);
      } catch (exc) {
        if (!active) return;
        setAssets(fallbackAssets);
        setError(exc instanceof Error ? exc.message : "API unavailable; showing demo fallback.");
      } finally {
        if (active) setIsLoading(false);
      }
    }

    void loadAssets();
    return () => {
      active = false;
    };
  }, [accessToken, fallbackAssets]);

  return (
    <div>
      <PageHeader
        eyebrow="Asset registry"
        title="Machines by risk and operating status"
        description="Live asset data is loaded through the backend and scoped by Supabase profile organization and plant."
      />
      {error ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
          Demo fallback active: {error}
        </div>
      ) : null}
      {isLoading ? (
        <EmptyState title="Loading assets" description="Fetching assigned plant machines from the backend." />
      ) : assets.length === 0 ? (
        <EmptyState title="No assets found" description="No machines are visible for this user and plant scope." />
      ) : (
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          {assets.map((asset) => (
            <div
              key={asset.id}
              className="grid gap-4 border-b border-slate-200 p-5 last:border-b-0 md:grid-cols-[1fr_auto_auto] dark:border-slate-800"
            >
              <div>
                <p className="font-semibold">{asset.name}</p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {asset.id} | {asset.line} | Plant: {asset.plant_id}
                </p>
              </div>
              <StatusBadge tone={toneForStatus(asset.status)}>{labelForStatus(asset.status)}</StatusBadge>
              <p className="text-sm font-semibold">Risk {Math.round(asset.risk_score * 100)}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
