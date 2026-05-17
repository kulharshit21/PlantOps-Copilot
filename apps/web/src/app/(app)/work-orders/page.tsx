"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/page-header";
import { apiFetch } from "@/lib/api";
import { workOrders as demoWorkOrders } from "@/lib/demo-data";
import { EmptyState, StatusBadge } from "@/lib/status";

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

function priorityTone(priority: string) {
  return priority === "urgent" || priority === "Urgent" ? "critical" : "watch";
}

export default function WorkOrdersPage() {
  const { accessToken } = useAuth();
  const [orders, setOrders] = useState<WorkOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fallbackOrders = useMemo<WorkOrder[]>(
    () =>
      demoWorkOrders.map((order, index) => ({
        id: `demo-wo-${index}`,
        asset_id: order.asset,
        title: order.title,
        status: order.status.toLowerCase(),
        priority: order.priority.toLowerCase(),
        assigned_role: "reliability_engineer",
        description: `Due ${order.due}`,
        audit_events: ["demo:fallback"],
      })),
    [],
  );

  const loadOrders = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiFetch<WorkOrder[]>("/work-orders", { accessToken });
      setOrders(data);
      setError(null);
    } catch (caught) {
      setOrders(fallbackOrders);
      setError(caught instanceof Error ? caught.message : "API unavailable; showing demo fallback.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, fallbackOrders]);

  useEffect(() => {
    const timeout = window.setTimeout(() => void loadOrders(), 0);
    return () => window.clearTimeout(timeout);
  }, [loadOrders]);

  async function transition(orderId: string, status: string) {
    try {
      await apiFetch<WorkOrder>(`/work-orders/${orderId}`, {
        method: "PATCH",
        accessToken,
        body: JSON.stringify({ status, note: `UI requested ${status}` }),
      });
      await loadOrders();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Status update failed.");
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Human review"
        title="AI-drafted work orders"
        description="Work orders are loaded from the backend and state changes are authorized server-side."
      />
      {error ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
          Demo fallback active: {error}
        </div>
      ) : null}
      {isLoading ? (
        <EmptyState title="Loading work orders" description="Fetching assigned plant work-order drafts." />
      ) : orders.length === 0 ? (
        <EmptyState title="No work orders found" description="Drafts from triage will appear here for review." />
      ) : (
        <div className="grid gap-4">
          {orders.map((order) => (
            <article
              key={order.id}
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold">{order.title}</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {order.asset_id} | assigned to {order.assigned_role}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <StatusBadge tone={priorityTone(order.priority)}>{order.priority}</StatusBadge>
                  <StatusBadge tone={order.status === "approved" ? "healthy" : "watch"}>
                    {order.status}
                  </StatusBadge>
                </div>
              </div>
              <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-950 dark:text-slate-300">
                {order.description || "No description provided."}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => void transition(order.id, "review")}
                  className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
                >
                  Mark review
                </button>
                <button
                  type="button"
                  onClick={() => void transition(order.id, "approved")}
                  className="rounded-md bg-teal-600 px-3 py-2 text-sm font-semibold text-white hover:bg-teal-700"
                >
                  Approve
                </button>
                <button
                  type="button"
                  onClick={() => void transition(order.id, "closed")}
                  className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
                >
                  Close
                </button>
              </div>
              <p className="mt-4 text-xs text-slate-500">
                Audit events: {order.audit_events.join(" | ") || "pending backend audit"}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
