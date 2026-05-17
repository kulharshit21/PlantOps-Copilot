"use client";

import { Activity, ArrowRight, ShieldCheck } from "lucide-react";
import { FormEvent, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { demoUsers, roleLabels, type UserRole } from "@/lib/demo-data";

export default function LoginPage() {
  const { isDemoMode, signInWithDemoRole, signInWithPassword } = useAuth();
  const [email, setEmail] = useState("asha.supervisor@example.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(await signInWithPassword(email, password));
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-white">
      <div className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl items-center gap-10 lg:grid-cols-[0.95fr_1.05fr]">
        <section>
          <div className="mb-6 flex size-12 items-center justify-center rounded-lg bg-teal-600">
            <Activity aria-hidden="true" size={24} />
          </div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-300">
            Secure plant intelligence
          </p>
          <h1 className="mt-4 text-5xl font-semibold leading-tight">
            Sign in to the PlantOps command center.
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            Role-aware UI for technicians, reliability engineers, supervisors,
            and admins. Database authorization remains enforced by Supabase RLS.
          </p>
          <div className="mt-8 rounded-lg border border-teal-800 bg-teal-950/50 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-teal-200">
              <ShieldCheck aria-hidden="true" size={16} />
              Frontend roles only hide or show navigation.
            </div>
            <p className="mt-2 text-sm text-slate-300">
              Backend checks and RLS remain source of truth for all protected data.
            </p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-800 bg-white p-6 text-slate-950 shadow-2xl shadow-black/30 dark:bg-slate-900 dark:text-white">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-2xl font-semibold">Access workspace</h2>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                {isDemoMode
                  ? "Supabase env vars missing; demo login is active."
                  : "Use Supabase email/password auth."}
              </p>
            </div>
            <span className="rounded-md bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 ring-1 ring-amber-200 dark:bg-amber-950 dark:text-amber-200 dark:ring-amber-800">
              {isDemoMode ? "Demo mode" : "Cloud mode"}
            </span>
          </div>

          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <label className="block">
              <span className="text-sm font-medium">Email</span>
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-2 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none ring-teal-600 transition focus:ring-2 dark:border-slate-700 dark:bg-slate-950"
                type="email"
              />
            </label>
            <label className="block">
              <span className="text-sm font-medium">Password</span>
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="mt-2 h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none ring-teal-600 transition focus:ring-2 dark:border-slate-700 dark:bg-slate-950"
                type="password"
                placeholder={isDemoMode ? "Demo mode does not require password" : ""}
              />
            </label>
            {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}
            <button
              type="submit"
              className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-4 text-sm font-semibold text-white hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
            >
              Continue
              <ArrowRight aria-hidden="true" size={16} />
            </button>
          </form>

          <div className="mt-6 border-t border-slate-200 pt-6 dark:border-slate-800">
            <p className="mb-3 text-sm font-semibold">Demo role switcher</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {demoUsers.map((demoUser) => (
                <button
                  key={demoUser.role}
                  type="button"
                  onClick={() => signInWithDemoRole(demoUser.role as UserRole)}
                  className="rounded-md border border-slate-200 bg-slate-50 px-3 py-3 text-left text-sm transition hover:border-teal-300 hover:bg-teal-50 dark:border-slate-800 dark:bg-slate-950 dark:hover:border-teal-800 dark:hover:bg-teal-950"
                >
                  <span className="font-semibold">{roleLabels[demoUser.role]}</span>
                  <span className="mt-1 block text-xs text-slate-500">
                    {demoUser.name}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
