import { PageHeader } from "@/components/page-header";
import { incidents } from "@/lib/demo-data";
import { StatusBadge } from "@/lib/status";

export default function IncidentsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Incident triage"
        title="Open plant incidents"
        description="Track operator reports, telemetry anomalies, and triage status for assigned plant assets."
      />
      <div className="grid gap-4">
        {incidents.map((incident) => (
          <article
            key={incident.title}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold">{incident.title}</p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {incident.asset} | {incident.time}
                </p>
              </div>
              <StatusBadge tone={incident.tone}>{incident.severity}</StatusBadge>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300">
              {incident.summary}
            </p>
          </article>
        ))}
      </div>
    </div>
  );
}
