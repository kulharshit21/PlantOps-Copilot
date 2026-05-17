"use client";

import { useState } from "react";
import { Bot, ChevronDown, ClipboardList, FileText, Gauge, Send, ShieldCheck } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/lib/status";

type RetrievedChunk = {
  chunk_id: string;
  document_id: string | null;
  title: string;
  content: string;
  source_uri: string;
  source_page: number | null;
  score: number | null;
};

type RagResponse = {
  answer: string;
  recommendation: string;
  urgency: string;
  next_steps: string[];
  citations: RetrievedChunk[];
  retrieved_chunks: RetrievedChunk[];
  model_used: string;
  fallback_used: boolean;
  confidence_notes: string;
};

type TriageResponse = {
  issue_summary: string;
  urgency: string;
  risk_score: number;
  likely_failure_mode: string;
  recommended_actions: string[];
  safety_checks: string[];
  parts_tools_needed: string[];
  drafted_work_order: {
    title: string;
    priority: string;
    description: string;
    acceptance_criteria: string[];
  };
  model_used: string;
};

const demoQuestion =
  "Line 2 spindle torque is high, tool wear is rising, and the operator reported vibration. What should the next shift do?";

const fallbackResponse: RagResponse = {
  answer:
    "Pause the job, apply lockout/tagout before inspection, inspect tool holder runout and lubrication, then schedule a bearing inspection before the next shift.",
  recommendation:
    "Pause the Line 2 spindle job and create a high-priority inspection work order.",
  urgency: "high",
  next_steps: [
    "Capture torque, vibration, tool-wear, and temperature readings.",
    "Apply lockout/tagout before opening guards.",
    "Inspect tool holder runout, lubrication, and bearing noise.",
    "Attach cited SOP evidence to the work order.",
  ],
  citations: [
    {
      chunk_id: "seed-spindle-vibration",
      document_id: "seed-doc-spindle",
      title: "Spindle vibration SOP",
      content:
        "When CNC spindle vibration rises together with torque load and tool wear, stop the active job at the next safe pause.",
      source_uri: "seed://sop/spindle-vibration",
      source_page: 1,
      score: 0.91,
    },
    {
      chunk_id: "seed-loto",
      document_id: "seed-doc-loto",
      title: "Lockout tagout safety note",
      content:
        "Before spindle housing inspection, isolate electrical and stored mechanical energy. Apply lockout/tagout.",
      source_uri: "seed://safety/loto",
      source_page: 1,
      score: 0.74,
    },
  ],
  retrieved_chunks: [],
  model_used: "local-ui-fallback",
  fallback_used: true,
  confidence_notes: "API unavailable; showing bundled demo evidence.",
};

export default function CopilotPage() {
  const [question, setQuestion] = useState(demoQuestion);
  const [result, setResult] = useState<RagResponse>(fallbackResponse);
  const [loading, setLoading] = useState(false);
  const [triageLoading, setTriageLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState(true);
  const [triage, setTriage] = useState<TriageResponse | null>(null);

  async function askCopilot() {
    setLoading(true);
    setError(null);
    try {
      const apiBaseUrl =
        process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
      const response = await fetch(`${apiBaseUrl}/rag/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 4 }),
      });
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      setResult((await response.json()) as RagResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to reach API");
      setResult(fallbackResponse);
    } finally {
      setLoading(false);
    }
  }

  async function runTriage() {
    setTriageLoading(true);
    setError(null);
    try {
      const apiBaseUrl =
        process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
      const response = await fetch(`${apiBaseUrl}/triage/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          asset_id: "asset-line-2-spindle",
          telemetry: {
            torque_nm: 104,
            tool_wear_min: 220,
            vibration_mm_s: 9.4,
            temperature_c: 78,
          },
          incident_notes: "Operator reported vibration during shift handoff.",
        }),
      });
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      setTriage((await response.json()) as TriageResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to run triage");
    } finally {
      setTriageLoading(false);
    }
  }

  const citations = result.citations.length ? result.citations : fallbackResponse.citations;

  return (
    <div>
      <PageHeader
        eyebrow="RAG copilot"
        title="Line 2 spindle triage"
        description="Grounded recommendations with source chunks, model fallback state, and review-ready next steps."
      />

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">
                Supervisor question
              </p>
              <h2 className="mt-1 text-xl font-semibold">Ask with evidence</h2>
            </div>
            <button
              type="button"
              onClick={() => setQuestion(demoQuestion)}
              className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              Run Line 2 demo
            </button>
          </div>

          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            className="mt-4 min-h-36 w-full resize-none rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm leading-6 outline-none ring-teal-500 transition focus:ring-2 dark:border-slate-800 dark:bg-slate-950"
          />

          <button
            type="button"
            onClick={askCopilot}
            disabled={loading}
            className="mt-4 inline-flex items-center gap-2 rounded-md bg-teal-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Send className="h-4 w-4" />
            {loading ? "Asking..." : "Ask copilot"}
          </button>
          <button
            type="button"
            onClick={runTriage}
            disabled={triageLoading}
            className="ml-3 mt-4 inline-flex items-center gap-2 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <ClipboardList className="h-4 w-4" />
            {triageLoading ? "Running..." : "Run triage"}
          </button>

          {error ? (
            <p className="mt-3 text-sm text-amber-600 dark:text-amber-300">
              API fallback active: {error}
            </p>
          ) : null}

          <div className="mt-6 rounded-lg border border-teal-200 bg-teal-50 p-5 dark:border-teal-900 dark:bg-teal-950">
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge tone={result.urgency === "high" ? "critical" : "watch"}>
                {result.urgency.toUpperCase()}
              </StatusBadge>
              <StatusBadge tone={result.fallback_used ? "watch" : "healthy"}>
                {result.fallback_used ? "Fallback used" : "Primary path"}
              </StatusBadge>
              <StatusBadge tone="neutral">{result.model_used}</StatusBadge>
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-3">
              <Metric icon={Bot} label="Recommendation" value={result.recommendation} />
              <Metric icon={Gauge} label="Urgency" value={result.urgency} />
              <Metric icon={ShieldCheck} label="Grounding" value={result.confidence_notes} />
            </div>
            <div className="mt-5">
              <h3 className="text-sm font-semibold">Next steps</h3>
              <ol className="mt-3 space-y-2 text-sm text-slate-700 dark:text-slate-200">
                {result.next_steps.map((step, index) => (
                  <li key={step} className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white text-xs font-bold text-teal-700 dark:bg-slate-900">
                      {index + 1}
                    </span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>

          {triage ? (
            <div className="mt-5 rounded-lg border border-blue-200 bg-blue-50 p-5 dark:border-blue-900 dark:bg-blue-950">
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge tone="critical">{triage.urgency.toUpperCase()}</StatusBadge>
                <StatusBadge tone="watch">Risk {Math.round(triage.risk_score * 100)}%</StatusBadge>
                <StatusBadge tone="neutral">{triage.model_used}</StatusBadge>
              </div>
              <h3 className="mt-4 font-semibold">{triage.drafted_work_order.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
                {triage.issue_summary}
              </p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div>
                  <p className="text-xs font-semibold uppercase text-slate-500">
                    Recommended actions
                  </p>
                  <ul className="mt-2 space-y-1 text-sm text-slate-700 dark:text-slate-200">
                    {triage.recommended_actions.map((action) => (
                      <li key={action}>- {action}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase text-slate-500">
                    Safety checks
                  </p>
                  <ul className="mt-2 space-y-1 text-sm text-slate-700 dark:text-slate-200">
                    {triage.safety_checks.map((check) => (
                      <li key={check}>- {check}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : null}
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <button
            type="button"
            onClick={() => setShowEvidence((value) => !value)}
            className="flex w-full items-center justify-between gap-3 text-left"
          >
            <span>
              <span className="block text-sm font-semibold text-slate-500 dark:text-slate-400">
                Why this answer?
              </span>
              <span className="mt-1 block text-xl font-semibold">Evidence panel</span>
            </span>
            <ChevronDown
              className={`h-5 w-5 transition ${showEvidence ? "rotate-180" : ""}`}
            />
          </button>

          {showEvidence ? (
            <div className="mt-4 space-y-3">
              {citations.map((citation) => (
                <div
                  key={citation.chunk_id}
                  className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm dark:border-slate-800 dark:bg-slate-950"
                >
                  <div className="flex items-start gap-3">
                    <FileText className="mt-0.5 h-4 w-4 text-teal-600" />
                    <div>
                      <p className="font-semibold">{citation.title}</p>
                      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                        {citation.source_uri}
                        {citation.source_page ? ` · page ${citation.source_page}` : ""}
                        {citation.score ? ` · score ${citation.score}` : ""}
                      </p>
                      <p className="mt-3 leading-6 text-slate-600 dark:text-slate-300">
                        {citation.content}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Bot;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-white p-4 dark:bg-slate-900">
      <Icon className="h-4 w-4 text-teal-600" />
      <p className="mt-3 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
        {label}
      </p>
      <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
        {value}
      </p>
    </div>
  );
}
