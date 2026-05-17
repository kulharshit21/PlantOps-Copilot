import { PageHeader } from "@/components/page-header";
import { workOrders } from "@/lib/demo-data";
import { StatusBadge } from "@/lib/status";

export default function WorkOrdersPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Human review"
        title="AI-drafted work orders"
        description="Supervisors can review, approve, and schedule AI recommendations. Frontend visibility is not authorization."
      />
      <div className="grid gap-4">
        {workOrders.map((order) => (
          <article
            key={order.title}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold">{order.title}</p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {order.asset} | Due {order.due}
                </p>
              </div>
              <StatusBadge tone={order.priority === "Urgent" ? "critical" : "watch"}>
                {order.priority}
              </StatusBadge>
            </div>
            <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-950 dark:text-slate-300">
              Status: {order.status}. Approval controls will connect to backend
              policy checks in a later phase.
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
