"use client";

import { Activity, LogOut, Menu } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { navigationItems, roleLabels, roleNavigation } from "@/lib/demo-data";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, isDemoMode, isLoading, isAuthenticated, signOut } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const allowed = roleNavigation[user.role];
  const visibleNav = navigationItems.filter((item) => allowed.includes(item.href));

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4 text-sm">
          Checking PlantOps session...
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4 text-sm">
          Redirecting to login...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950 dark:bg-slate-950 dark:text-white">
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-72 border-r border-slate-200 bg-white p-5 transition lg:translate-x-0 dark:border-slate-800 dark:bg-slate-900 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-lg bg-teal-600 text-white">
            <Activity aria-hidden="true" size={21} />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700 dark:text-teal-300">
              PlantOps
            </p>
            <p className="font-semibold">Copilot</p>
          </div>
        </div>

        <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950">
          <p className="text-sm font-semibold">{user.name}</p>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {roleLabels[user.role]} | {user.plant}
          </p>
          {isDemoMode ? (
            <p className="mt-3 rounded-md bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-700 ring-1 ring-amber-200 dark:bg-amber-950 dark:text-amber-200 dark:ring-amber-800">
              Demo mode
            </p>
          ) : null}
        </div>

        <nav className="mt-6 space-y-1">
          {visibleNav.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-slate-950 text-white dark:bg-white dark:text-slate-950"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                }`}
                onClick={() => setIsOpen(false)}
              >
                <Icon aria-hidden="true" size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <button
          type="button"
          onClick={() => void signOut()}
          className="absolute bottom-5 left-5 right-5 inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          <LogOut aria-hidden="true" size={16} />
          Sign out
        </button>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setIsOpen(true)}
              className="rounded-md border border-slate-300 p-2 lg:hidden dark:border-slate-700"
              aria-label="Open navigation"
            >
              <Menu aria-hidden="true" size={18} />
            </button>
            <div className="hidden lg:block">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {user.organization}
              </p>
              <p className="font-semibold">{user.plant} command center</p>
            </div>
            <Link
              href="/copilot"
              className="rounded-md bg-teal-600 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-700"
            >
              Run demo triage
            </Link>
          </div>
        </header>
        <main className="px-5 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
