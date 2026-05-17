"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/page-header";
import { apiFetch } from "@/lib/api";
import type { StatusTone } from "@/lib/demo-data";
import { EmptyState, StatusBadge } from "@/lib/status";

type SecurityReadiness = {
  auth_configured: boolean;
  demo_mode: boolean;
  supabase_reachable: boolean;
  rls_migration_files_detected: boolean;
  audit_logs_table_reachable: boolean;
  rag_citation_test_status: string;
  work_order_persistence_status: string;
  notes: string[];
};

function tone(pass: boolean): StatusTone {
  return pass ? "healthy" : "watch";
}

export default function SecurityPage() {
  const { accessToken } = useAuth();
  const [readiness, setReadiness] = useState<SecurityReadiness | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function loadReadiness() {
      try {
        const data = await apiFetch<SecurityReadiness>("/security/readiness", { accessToken });
        if (!active) return;
        setReadiness(data);
        setError(null);
      } catch (caught) {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : "Security readiness unavailable.");
      }
    }
    void loadReadiness();
    return () => {
      active = false;
    };
  }, [accessToken]);

  const checks = readiness
    ? [
        ["Auth configured", readiness.auth_configured],
        ["Demo mode disabled for live", !readiness.demo_mode],
        ["Supabase reachable", readiness.supabase_reachable],
        ["RLS migrations detected", readiness.rls_migration_files_detected],
        ["Audit logs reachable", readiness.audit_logs_table_reachable],
        ["RAG citation tests", readiness.rag_citation_test_status === "covered-by-tests"],
        ["Work-order persistence tests", readiness.work_order_persistence_status === "covered-by-tests"],
      ]
    : [];

  return (
    <div>
      <PageHeader
        eyebrow="DevSecOps"
        title="Security proof"
        description="Live readiness checks for auth, Supabase reachability, RLS files, audit logs, and eval smoke tests."
      />
      {error ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
          Readiness warning: {error}
        </div>
      ) : null}
      {!readiness ? (
        <EmptyState title="Loading security readiness" description="Fetching live backend proof checks." />
      ) : (
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">RLS and access posture</h2>
            <StatusBadge tone={readiness.demo_mode ? "watch" : "healthy"}>
              {readiness.demo_mode ? "Demo mode" : "Live mode"}
            </StatusBadge>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {checks.map(([label, pass]) => (
              <div key={String(label)} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-950">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium">{label}</p>
                  <StatusBadge tone={tone(Boolean(pass))}>{pass ? "Pass" : "Check"}</StatusBadge>
                </div>
              </div>
            ))}
          </div>
          {readiness.notes.length ? (
            <div className="mt-4 rounded-lg bg-amber-50 p-4 text-sm text-amber-800 dark:bg-amber-950 dark:text-amber-200">
              {readiness.notes.map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          ) : null}
        </section>
      )}
    </div>
  );
}
