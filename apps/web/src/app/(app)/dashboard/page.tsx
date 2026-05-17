import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import {
  assets,
  incidents,
  quickActions,
  systemStatus,
  workOrders,
} from "@/lib/demo-data";
import { StatusBadge } from "@/lib/status";

export default function DashboardPage() {
  const criticalAssets = assets.filter((asset) => asset.tone === "critical");
  const healthyCount = assets.filter((asset) => asset.tone === "healthy").length;
  const watchCount = assets.filter((asset) => asset.tone === "watch").length;

  return (
    <div>
      <PageHeader
        eyebrow="Supervisor overview"
        title="Plant health dashboard"
        description="Shift-ready view of asset risk, active incidents, AI work-order drafts, and system trust signals."
        action={
          <Link
            href="/copilot"
            className="inline-flex h-11 items-center justify-center rounded-md bg-teal-600 px-4 text-sm font-semibold text-white hover:bg-teal-700"
          >
            Ask copilot about Line 2
          </Link>
        }
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {[
          ["Total assets", assets.length.toString(), "Across assigned plant"],
          ["Critical assets", criticalAssets.length.toString(), "Immediate review"],
          ["Watch assets", watchCount.toString(), "Monitor next shift"],
          ["Healthy assets", healthyCount.toString(), "Normal operation"],
        ].map(([label, value, caption]) => (
          <article
            key={label}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
              {label}
            </p>
            <p className="mt-3 text-3xl font-semibold">{value}</p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{caption}</p>
          </article>
        ))}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">High-risk assets</h2>
            <StatusBadge tone="critical">Critical</StatusBadge>
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
                    <StatusBadge tone={asset.tone}>{asset.status}</StatusBadge>
                  </div>
                  <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                    {asset.id} | {asset.line} | {asset.signal}
                  </p>
                </div>
                <div className="min-w-32 text-right">
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                    Risk
                  </p>
                  <p className="text-2xl font-semibold">{asset.risk}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-semibold">System status</h2>
          <div className="mt-4 space-y-3">
            {systemStatus.map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3 dark:bg-slate-950"
              >
                <p className="text-sm font-medium">{item.label}</p>
                <StatusBadge tone={item.tone}>{item.value}</StatusBadge>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-semibold">Recent incidents</h2>
          <div className="mt-4 space-y-3">
            {incidents.map((incident) => (
              <div key={incident.title} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-950">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{incident.title}</p>
                  <StatusBadge tone={incident.tone}>{incident.severity}</StatusBadge>
                </div>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {incident.asset} | {incident.time}
                </p>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                  {incident.summary}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-lg font-semibold">Pending work orders</h2>
          <div className="mt-4 space-y-3">
            {workOrders.map((order) => (
              <div key={order.title} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-950">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{order.title}</p>
                  <StatusBadge tone={order.priority === "Urgent" ? "critical" : "watch"}>
                    {order.priority}
                  </StatusBadge>
                </div>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                  {order.asset} | {order.status} | {order.due}
                </p>
              </div>
            ))}
          </div>
        </div>
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
    </div>
  );
}
