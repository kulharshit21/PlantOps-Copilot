# Demo Script

## Setup

The demo starts with seed assets, synthetic SOP/manual chunks, synthetic work-order history, and local fallback services configured. External Mistral and Supabase paths can be enabled later with real credentials stored outside git.

## Main Scenario

1. Supervisor logs in.
2. Dashboard highlights `Line 2 Spindle` as high risk.
3. Supervisor asks: `Line 2 spindle torque is high, tool wear is rising, and the operator reported vibration. What should the next shift do?`
4. Copilot retrieves cited SOP/manual/work-order evidence.
5. Predictive model returns a failure-risk score and likely contributing factors.
6. Agent returns structured JSON with issue classification, urgency, evidence, recommended actions, and work-order draft.
7. UI renders the recommendation, citations, timeline, and `Why this answer?` panel.
8. Supervisor reviews the work order.
9. Observability page shows latency, errors, RAG hit/miss, selected model, and fallback status.
10. Security proof page shows RLS posture, role access notes, audit trail, and CI/security scan proof.

## Backup Path

If cloud APIs are unavailable, the demo uses Ollama/local mock providers and seed data. The product should still show the complete decision workflow, citations, risk score, and proof pages.
