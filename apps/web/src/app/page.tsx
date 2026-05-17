import {
  Activity,
  ArrowRight,
  Bot,
  ClipboardCheck,
  DatabaseZap,
  Gauge,
  LineChart,
  ShieldCheck,
} from "lucide-react";

const capabilities = [
  {
    title: "RAG with citations",
    description:
      "Search SOPs, manuals, and work history with evidence panels technicians can verify.",
    icon: DatabaseZap,
    accent: "text-teal-600 dark:text-teal-300",
  },
  {
    title: "ML failure risk",
    description:
      "Score asset risk from tool wear, torque, vibration reports, and maintenance signals.",
    icon: LineChart,
    accent: "text-emerald-600 dark:text-emerald-300",
  },
  {
    title: "Agentic triage",
    description:
      "Classify incidents, retrieve procedures, score urgency, and draft reviewable work orders.",
    icon: Bot,
    accent: "text-blue-600 dark:text-blue-300",
  },
  {
    title: "DevSecOps proof",
    description:
      "Show role access, RLS posture, audit trails, secret scans, and dependency checks.",
    icon: ShieldCheck,
    accent: "text-cyan-600 dark:text-cyan-300",
  },
  {
    title: "Ops observability",
    description:
      "Track latency, errors, model fallback, retrieval hit rate, and service health.",
    icon: Gauge,
    accent: "text-sky-600 dark:text-sky-300",
  },
];

const healthSignals = [
  ["Line 2 Spindle", "High risk", "Torque + vibration"],
  ["RAG status", "Ready", "4 cited chunks"],
  ["Fallback", "Armed", "Ollama local mode"],
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-white">
      <section className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-teal-600 text-white shadow-sm shadow-teal-700/20">
              <Activity aria-hidden="true" size={22} />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700 dark:text-teal-300">
                PlantOps
              </p>
              <p className="text-lg font-semibold">Copilot</p>
            </div>
          </div>
          <a
            href="/login"
            className="inline-flex h-10 items-center gap-2 rounded-md bg-slate-950 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
          >
            Demo path
            <ArrowRight aria-hidden="true" size={16} />
          </a>
        </div>
      </section>

      <section className="mx-auto grid w-full max-w-7xl gap-10 px-6 py-16 lg:grid-cols-[1.05fr_0.95fr] lg:py-20">
        <div className="flex flex-col justify-center">
          <div className="mb-6 inline-flex w-fit items-center gap-2 rounded-md border border-teal-200 bg-teal-50 px-3 py-2 text-sm font-medium text-teal-800 dark:border-teal-800 dark:bg-teal-950 dark:text-teal-200">
            <ShieldCheck aria-hidden="true" size={16} />
            Secure predictive maintenance for industrial teams
          </div>
          <h1 className="max-w-4xl text-5xl font-semibold leading-tight text-slate-950 dark:text-white">
            AI shift handoff command center for machine risk, evidence, and
            next action.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
            PlantOps Copilot combines cited SOP retrieval, predictive
            maintenance ML, structured AI recommendations, observability, and
            DevSecOps proof into one supervisor-ready workflow.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <a
              href="/login"
              className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-teal-600 px-5 text-sm font-semibold text-white shadow-sm shadow-teal-700/20 transition hover:bg-teal-700"
            >
              Run demo scenario
              <ArrowRight aria-hidden="true" size={18} />
            </a>
            <a
              href="/dashboard"
              className="inline-flex h-12 items-center justify-center rounded-md border border-slate-300 bg-white px-5 text-sm font-semibold text-slate-800 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
            >
              Open dashboard
            </a>
          </div>
        </div>

        <div
          id="demo"
          className="rounded-lg border border-slate-200 bg-white p-5 shadow-xl shadow-slate-200/70 dark:border-slate-800 dark:bg-slate-900 dark:shadow-black/30"
        >
          <div className="flex items-start justify-between gap-4 border-b border-slate-200 pb-5 dark:border-slate-800">
            <div>
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Demo asset
              </p>
              <h2 className="mt-1 text-2xl font-semibold">Line 2 Spindle</h2>
            </div>
            <span className="rounded-md bg-red-50 px-3 py-1 text-sm font-semibold text-red-700 ring-1 ring-red-200 dark:bg-red-950 dark:text-red-200 dark:ring-red-800">
              High risk
            </span>
          </div>

          <div className="mt-5 space-y-3">
            {healthSignals.map(([name, state, detail]) => (
              <div
                key={name}
                className="grid grid-cols-[1fr_auto] gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950"
              >
                <div>
                  <p className="font-medium">{name}</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {detail}
                  </p>
                </div>
                <p className="text-sm font-semibold text-teal-700 dark:text-teal-300">
                  {state}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-5 rounded-lg bg-slate-950 p-5 text-white dark:bg-black">
            <div className="mb-4 flex items-center gap-2 text-sm font-medium text-teal-200">
              <ClipboardCheck aria-hidden="true" size={16} />
              AI recommendation draft
            </div>
            <p className="text-sm leading-6 text-slate-200">
              Reduce spindle load, inspect tool wear and bearing vibration,
              schedule next-shift work order, and cite SOP lockout plus spindle
              anomaly procedure before maintenance begins.
            </p>
          </div>
        </div>
      </section>

      <section
        id="capabilities"
        className="border-t border-slate-200 bg-slate-100 px-6 py-16 dark:border-slate-800 dark:bg-slate-900"
      >
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-teal-700 dark:text-teal-300">
              System capabilities
            </p>
            <h2 className="mt-3 text-3xl font-semibold text-slate-950 dark:text-white">
              Built for credible hackathon proof, not slideware.
            </h2>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            {capabilities.map((item) => {
              const Icon = item.icon;

              return (
                <article
                  key={item.title}
                  className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950"
                >
                  <Icon className={item.accent} aria-hidden="true" size={28} />
                  <h3 className="mt-5 text-lg font-semibold">{item.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-400">
                    {item.description}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}
