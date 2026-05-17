# PlantOps Copilot

Secure AI maintenance copilot for industrial teams: RAG over SOPs/manuals, predictive failure-risk ML, agentic work-order drafting, LLMOps/MLOps evaluation, observability, and DevSecOps.

## Project Pitch

PlantOps Copilot helps technicians, reliability engineers, and supervisors answer the maintenance questions that matter during a shift handoff:

- What is happening to this machine?
- What evidence supports the answer?
- What should the next shift do?
- How urgent is it?
- Can the system prove that it is secure, monitored, and reliable?

The hackathon value is a production-minded demo path: a supervisor can inspect a risky asset, ask an operational question, receive cited SOP/manual evidence, see a failure-risk score, review an AI-drafted work order, and verify security and observability proof points.

## Architecture Overview

PlantOps Copilot is planned as a monorepo with a Next.js frontend, FastAPI backend, Supabase data plane, RAG pipeline, predictive-maintenance ML service, and DevSecOps/AIOps support assets.

High-level flow:

1. Users authenticate and access role-aware dashboards.
2. SOPs, manuals, and work-order records are ingested, chunked, embedded, and stored with citations.
3. Chat and triage requests retrieve relevant chunks through vector search.
4. The backend calls an LLM provider adapter, preferring Mistral cloud mode and falling back to Ollama local mode.
5. Predictive ML scores asset failure risk using an AI4I-trained scikit-learn model.
6. Agentic triage returns structured JSON recommendations and a UI-rendered work-order draft.
7. Observability, evaluation, and security pages prove latency, fallback status, retrieval quality, ML metrics, RLS posture, and CI/security checks.

## Stack

- Monorepo: apps, packages, ML, ops, evals, Supabase migrations
- Frontend: Next.js, TypeScript, Tailwind CSS, shadcn/ui-style components
- Backend: FastAPI, Python, Pydantic models
- Auth/DB/Storage/Vector DB: Supabase free tier, Postgres, Auth, Storage, pgvector, Row Level Security
- RAG: ingestion, chunking, embeddings, vector search, citations
- LLMs: Mistral API primary, Ollama Gemma local fallback
- Embeddings: local Ollama EmbeddingGemma if available, otherwise provider adapter
- Agents: PydanticAI-style typed agent service or compatible typed service
- ML: scikit-learn predictive maintenance model trained on AI4I 2020
- MLOps: MLflow tracking and model artifacts
- LLMOps/RAG eval: Evidently-style or lightweight local evaluation scripts
- Observability: OpenTelemetry, Prometheus metrics, Grafana-ready config
- DevSecOps: GitHub Actions, tests, linting, Gitleaks, Trivy, dependency checks

## Local Setup

Install frontend dependencies and backend test dependencies:

```bash
cp .env.example .env
cd apps/web
npm install
cd ../api
python -m pip install -e ".[dev]"
```

Run local checks:

```bash
npm run lint
npm run build
python -m pytest apps/api/tests
docker compose config
```

Train the predictive-maintenance baseline when the AI4I CSV is available:

```bash
python ml/training/train_failure_model.py --data ml/data/ai4i2020.csv
```

API foundation endpoints:

```text
GET  /health
GET  /version
GET  /assets
GET  /incidents
GET  /documents
POST /documents/ingest
POST /rag/ask
POST /risk/predict
POST /triage/run
GET  /work-orders
POST /work-orders
GET  /ops/metrics-summary
```

Start the API locally:

```bash
docker compose up api
```

Open the web demo at `/login`. If Supabase public env vars are absent, the app uses a local demo role switcher so the hackathon flow still works.

No real secrets should be committed. Browser-safe variables must use public-safe values only, and server-only keys must stay in backend runtime environments.

## Main Demo Scenario

A supervisor logs in and sees `Line 2 Spindle` marked high risk. They ask:

> Line 2 spindle torque is high, tool wear is rising, and the operator reported vibration. What should the next shift do?

The system retrieves SOP/manual/work-order chunks, predicts failure risk, explains the likely failure mode, assigns urgency, drafts a work order, cites evidence, logs traces and metrics, and shows security/CI proof for the demo.

The `/copilot` page can run this scenario against the FastAPI `/rag/ask` endpoint. If the API is offline, it falls back to bundled demo evidence so the pitch path remains presentable.

## Roadmap

- Phase 0: Repository planning and safety baseline
- Phase 1: Monorepo app scaffolding and local developer workflow
- Phase 2: Supabase schema, RLS policies, seed data, and backend DB config
- Phase 3: Next.js dashboard, asset registry, and demo workflow UI
- Phase 4: Typed FastAPI foundation and protected API contracts
- Phase 5: Document ingestion, chunking, and RAG retrieval foundation
- Phase 6: Cited RAG answer endpoint and model fallback
- Phase 7: Predictive maintenance ML training and scoring endpoint
- Phase 8: Agentic triage and structured work-order drafting
- Phase 9: Work-order lifecycle and audit trail
- Phase 10: Observability, metrics, traces, and operational health UI
- Phase 11: Evaluation dashboards for RAG, LLM, ML, and security checks
- Phase 12: CI, vulnerability scanning, secret scanning, and demo hardening
- Phase 13: Hackathon-grade UI/UX polish
- Phase 14: End-to-end demo seed and pitch script
- Phase 15: Final production-readiness review
