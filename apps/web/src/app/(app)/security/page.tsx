import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/lib/status";

const checks = [
  "RLS enabled on operational tables",
  "No service-role key in frontend env",
  "Role-aware UI is visibility only",
  "Backend and Supabase remain enforcement layer",
];

export default function SecurityPage() {
  return (
    <div>
      <PageHeader
        eyebrow="DevSecOps"
        title="Security proof"
        description="Demo proof for tenant isolation, plant scoping, frontend key boundaries, and audit-ready controls."
      />
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">RLS and access posture</h2>
          <StatusBadge tone="healthy">Pass</StatusBadge>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {checks.map((check) => (
            <div key={check} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-950">
              <p className="text-sm font-medium">{check}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
