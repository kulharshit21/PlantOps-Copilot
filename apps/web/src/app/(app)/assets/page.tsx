import { PageHeader } from "@/components/page-header";
import { assets } from "@/lib/demo-data";
import { StatusBadge } from "@/lib/status";

export default function AssetsPage() {
  return (
    <div>
      <PageHeader
        eyebrow="Asset registry"
        title="Machines by risk and operating status"
        description="Demo registry scoped to assigned plant data. Real access must be enforced by backend and Supabase RLS."
      />
      <div className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {assets.map((asset) => (
          <div
            key={asset.id}
            className="grid gap-4 border-b border-slate-200 p-5 last:border-b-0 md:grid-cols-[1fr_auto_auto] dark:border-slate-800"
          >
            <div>
              <p className="font-semibold">{asset.name}</p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                {asset.id} | {asset.line} | Owner: {asset.owner}
              </p>
            </div>
            <StatusBadge tone={asset.tone}>{asset.status}</StatusBadge>
            <p className="text-sm font-semibold">Risk {asset.risk}%</p>
          </div>
        ))}
      </div>
    </div>
  );
}
