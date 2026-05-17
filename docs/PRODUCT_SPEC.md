# Product Spec

## Product

PlantOps Copilot is a secure predictive-maintenance and SOP triage copilot for manufacturing teams. It combines role-aware dashboards, retrieval-augmented generation, predictive failure-risk scoring, and structured work-order drafting.

## Users

- Technician: needs clear next actions, safety steps, and cited procedures.
- Reliability Engineer: needs evidence, failure patterns, risk scores, and model/evaluation visibility.
- Supervisor/Admin: needs shift-level prioritization, reviewable work orders, access controls, and security proof.

## Core Jobs

- Identify what is happening to a machine from telemetry, operator notes, and work history.
- Retrieve relevant SOP/manual/work-order evidence.
- Predict failure risk and urgency.
- Draft a structured recommendation and work order for human review.
- Prove the system is monitored, evaluated, and secure.

## Demo Workflow

The supervisor sees `Line 2 Spindle` with high risk, asks a natural-language triage question, reviews cited evidence and ML risk, approves or edits a work-order draft, and opens security and observability proof pages.

## Success Criteria

- Every RAG answer includes citations.
- Every operational recommendation starts as structured JSON.
- External AI dependencies have a local fallback path.
- Sensitive data is protected by role-aware backend checks and Supabase RLS.
- Demo flows work with seed data.
