# Security

## Baseline Principles

- Never commit secrets, service-role keys, API tokens, passwords, or production `.env` files.
- Keep browser-visible environment variables public-safe.
- Keep privileged keys in backend-only runtime environments.
- Enable Supabase Row Level Security on sensitive tables.
- Return citations and structured outputs for operational recommendations.
- Log security-relevant events without logging secrets or sensitive raw documents.

## Data Boundaries

- Frontend: public anon keys and user session only.
- Backend: server-only provider credentials and privileged service access only when required.
- Supabase: RLS policies enforce tenant, role, and ownership boundaries.
- Storage: SOP/manual uploads are scoped by organization and access role.

## DevSecOps Controls

- Secret scanning with Gitleaks.
- Container and dependency scanning with Trivy or equivalent.
- CI for linting, tests, and build checks.
- `.env.example` with placeholder values only.
- `.gitignore` blocking generated artifacts, logs, local databases, and secret-bearing env files.

## Phase 0 Review

This phase creates documentation, empty project folders, `.gitignore`, and placeholder environment configuration only. It does not add application code, credentials, or data.

## Supabase RLS Design

PlantOps Copilot treats plant operations data as tenant-scoped and plant-scoped. Every operational table in the public schema has Row Level Security enabled, and policies are written for the `authenticated` role only. No policy grants anonymous public row access.

Authorization data lives in `public.profiles`, keyed by the Supabase Auth user id. Policies do not use `user_metadata`, because user-editable metadata is unsafe for authorization. Private helper functions in the non-exposed `app_private` schema resolve the current user's organization, assigned plants, and role. This keeps policies consistent while avoiding public security-definer functions.

Access model:

- Technicians can read data for assigned plants and create incidents/RAG queries for those plants.
- Reliability engineers share assigned-plant read access for evidence and predictions.
- Supervisors can create and update work orders for assigned plants.
- Admins can manage organization and plant data inside their organization.
- Audit logs are readable by organization admins and insertable only by authenticated users acting as themselves.

Threat model:

- Cross-tenant reads are blocked by `organization_id` checks.
- Cross-plant reads are blocked unless the user is assigned to the plant or is an organization admin.
- Browser clients must use only `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- `SUPABASE_SERVICE_ROLE_KEY` is backend-only and must never appear in frontend code or public environment variables.
- RLS remains the final database enforcement layer even if a backend route has a bug.

## Frontend Auth Shell

The Next.js role-aware shell uses Supabase browser auth when public Supabase environment variables are configured, and a demo-mode user switcher when they are missing. This role controls navigation visibility only. It is not an authorization boundary. Any data mutation or sensitive read must still pass backend checks and Supabase RLS policies.

## Backend API Boundary

The FastAPI foundation centralizes auth checks in `app/core/security.py`. In local demo mode, requests without bearer tokens receive a fixed demo supervisor identity so the pitch flow works offline. When `DEMO_MODE=false`, protected routes fail closed with `401 Authentication required`.

Live mode verifies bearer tokens with Supabase Auth and then loads role, organization, plant, and profile identity from `public.profiles`. The backend does not trust frontend role claims. Sensitive request metadata is masked before audit logging. Rate limiting is marked in `app/main.py` before routes that will call LLM providers or create operational records.

## Live RLS And Storage Updates

The live schema fix migration aligns database constraints with the API lifecycle:

- Asset status accepts `high_risk` for the demo asset while preserving existing operational states.
- Work orders accept `draft`, `review`, `approved`, `assigned`, and `closed` for the backend lifecycle.
- Seeded document chunks include `title`, `source_uri`, and `source_page`, matching the citation columns required by RAG.
- `match_document_chunks` prefers pgvector similarity, but can return scoped seed chunks with a low fallback score when embeddings have not been generated yet. This keeps demos honest: citations are real rows, while embedding quality is reported separately.

Storage object access is path-scoped. Objects must use:

```text
{organization_id}/{plant_id}/filename
```

Storage policies check the authenticated profile's organization and assigned plant before allowing reads or writes. The service-role key remains backend-only and must never be exposed to browser code.

## Supabase End-to-End Setup Notes

Codex MCP is authenticated for the project, but this running session does not expose Supabase MCP tools until restart. The repository carries deterministic migrations for schema, pgvector search, private storage buckets, storage object policies, and authenticated role grants. Apply migrations through Supabase MCP or CLI from a session with credentials loaded; never commit service-role keys or database passwords.

Required backend secrets:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET` or `SUPABASE_JWKS_URL` only if local JWT verification is used instead of Supabase Auth verification

Frontend must only receive `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.

Project URL is safe to expose. Service-role, JWT secret, database password, and provider API keys are not safe to expose and must stay out of git.
