# Architecture

## System Shape

PlantOps Copilot is a monorepo with separate frontend, backend, ML, evaluation, Supabase, and ops areas.

```text
apps/web        Next.js UI
apps/api        FastAPI service
packages/shared Shared schemas and generated types
ml              Training, reports, artifacts, and notebooks
supabase        Migrations, RLS policies, and seed SQL
ops             Docker, Prometheus, Grafana, and scripts
evals           RAG, ML, and security evaluation suites
```

## Runtime Flow

1. User authenticates through Supabase Auth.
2. Frontend calls the FastAPI backend with user context.
3. Backend enforces role-aware authorization and reads/writes through safe server-side clients.
4. RAG services retrieve cited SOP/manual/work-order chunks from pgvector-backed storage.
5. LLM provider adapters call Mistral first, then local Ollama fallback when configured.
6. Predictive maintenance scoring uses a scikit-learn model trained on AI4I-style features.
7. Agent service combines retrieval, risk scoring, and typed output schemas.
8. Observability emits traces, structured logs, and Prometheus metrics.

## Key Interfaces

- `LLMProvider`: cloud and local text generation adapters.
- `EmbeddingProvider`: local or cloud embedding adapters.
- `Retriever`: vector search with source chunk citations.
- `RiskModel`: predictive-maintenance inference contract.
- `TriageAgent`: typed operational recommendation contract.

## Backend API Foundation

The FastAPI service is split by responsibility:

```text
app/core       settings, auth dependencies, logging helpers
app/api/routes route modules grouped by product capability
app/schemas    Pydantic request/response contracts
app/services   demo-safe service layer and future provider adapters
app/models     persistence models placeholder
```

Protected routes use a shared `get_current_user` dependency. `DEMO_MODE=true` enables the local hackathon path without external Supabase auth. With `DEMO_MODE=false`, protected routes reject unauthenticated requests until Supabase JWT verification is completed.

## RAG Storage Foundation

Document ingestion accepts `.md`/`.txt` style text content through the backend, chunks it into citation-friendly passages, generates deterministic mock embeddings for local tests, and stores chunks in a scoped document store. Search always filters by organization and plant before returning citations. The Supabase migration adds richer chunk citation fields and a `match_document_chunks` RPC for pgvector cosine search when the hosted database is connected.

## Cited Answer Flow

`/rag/ask` retrieves scoped chunks first, then calls chat providers through a fallback chain: Mistral adapter, Ollama adapter, then deterministic mock provider for demo resilience. Responses separate recommendation, urgency, next steps, model used, fallback status, retrieved chunks, and citations so the UI can render evidence separately from actions.

## Deployment Direction

The hackathon target is local Docker Compose plus cloud-ready configuration. Supabase free tier is the planned hosted data plane, with local seed data supporting demos when external APIs are unavailable.
