import { PageHeader } from "@/components/page-header";
import type { StatusTone } from "@/lib/demo-data";
import { StatusBadge } from "@/lib/status";

const signals: Array<[string, string, StatusTone]> = [
  ["API latency p95", "182 ms", "healthy"],
  ["RAG hit rate", "Seed mode", "watch"],
  ["Fallback status", "Ollama armed", "healthy"],
  ["Error budget", "No demo errors", "healthy"],
];

export default function ObservabilityPage() {
  return (
    <div>
      <PageHeader
        eyebrow="AIOps"
        title="Operational health"
        description="Grafana-ready signals for latency, errors, RAG hit rate, model choice, and fallback state."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {signals.map(([label, value, tone]) => (
          <article
            key={label}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
            <p className="mt-3 text-2xl font-semibold">{value}</p>
            <div className="mt-4">
              <StatusBadge tone={tone}>Tracked</StatusBadge>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
