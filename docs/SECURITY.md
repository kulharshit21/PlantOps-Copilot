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
