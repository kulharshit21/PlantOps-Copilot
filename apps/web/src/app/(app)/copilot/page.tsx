import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/lib/status";

export default function CopilotPage() {
  return (
    <div>
      <PageHeader
        eyebrow="RAG copilot"
        title="Line 2 spindle triage"
        description="Demo path shows how the copilot will retrieve evidence, score risk, and draft a structured recommendation."
      />
      <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">
            Supervisor question
          </p>
          <div className="mt-3 rounded-lg bg-slate-100 p-4 text-sm leading-6 dark:bg-slate-950">
            Line 2 spindle torque is high, tool wear is rising, and the operator
            reported vibration. What should the next shift do?
          </div>
          <div className="mt-5 rounded-lg border border-teal-200 bg-teal-50 p-5 dark:border-teal-900 dark:bg-teal-950">
            <div className="flex items-center gap-2">
              <StatusBadge tone="critical">Urgent</StatusBadge>
              <StatusBadge tone="watch">Seed RAG</StatusBadge>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-700 dark:text-slate-200">
              Reduce feed rate, perform lockout-tagout, inspect tool wear and
              spindle vibration, record bearing temperature, and schedule an
              urgent next-shift work order before restart.
            </p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="font-semibold">Why this answer?</h2>
          <div className="mt-4 space-y-3">
            {["SOP-17#chunk-0", "SOP-17#chunk-1", "Manual-08#chunk-0"].map(
              (citation) => (
                <div
                  key={citation}
                  className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm dark:border-slate-800 dark:bg-slate-950"
                >
                  <p className="font-semibold">{citation}</p>
                  <p className="mt-2 text-slate-500 dark:text-slate-400">
                    Cited seed evidence for spindle vibration, lockout-tagout,
                    and early degradation response.
                  </p>
                </div>
              ),
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
