create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;
create extension if not exists vector with schema extensions;

create schema if not exists app_private;
revoke all on schema app_private from public;

create table public.organizations (
  id uuid primary key default extensions.gen_random_uuid(),
  name text not null,
  slug text not null unique,
  created_at timestamptz not null default now()
);

create table public.plants (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  name text not null,
  location text,
  created_at timestamptz not null default now(),
  unique (organization_id, name)
);

create table public.profiles (
  id uuid primary key default extensions.gen_random_uuid(),
  user_id uuid not null unique,
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid references public.plants(id) on delete set null,
  assigned_plant_ids uuid[] not null default '{}',
  role text not null check (role in ('technician', 'reliability_engineer', 'supervisor', 'admin')),
  display_name text not null,
  email text,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.assets (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid not null references public.plants(id) on delete cascade,
  created_by uuid references public.profiles(id) on delete set null,
  asset_tag text not null,
  name text not null,
  line_name text not null,
  status text not null check (status in ('healthy', 'watch', 'degraded', 'critical', 'offline')),
  risk_score numeric(5, 4) not null default 0 check (risk_score >= 0 and risk_score <= 1),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (organization_id, asset_tag)
);

create table public.incidents (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid not null references public.plants(id) on delete cascade,
  asset_id uuid not null references public.assets(id) on delete cascade,
  created_by uuid references public.profiles(id) on delete set null,
  title text not null,
  description text not null,
  severity text not null check (severity in ('low', 'medium', 'high', 'critical')),
  status text not null check (status in ('open', 'triaged', 'in_progress', 'resolved')),
  observed_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.documents (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid references public.plants(id) on delete cascade,
  created_by uuid references public.profiles(id) on delete set null,
  title text not null,
  document_type text not null check (document_type in ('sop', 'manual', 'work_order', 'safety', 'other')),
  storage_path text,
  source_uri text,
  checksum text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.document_chunks (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid references public.plants(id) on delete cascade,
  document_id uuid not null references public.documents(id) on delete cascade,
  created_by uuid references public.profiles(id) on delete set null,
  chunk_index integer not null check (chunk_index >= 0),
  content text not null,
  citation_label text not null,
  page_number integer,
  embedding extensions.vector(768),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (document_id, chunk_index)
);

create table public.work_orders (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid not null references public.plants(id) on delete cascade,
  asset_id uuid not null references public.assets(id) on delete cascade,
  incident_id uuid references public.incidents(id) on delete set null,
  created_by uuid references public.profiles(id) on delete set null,
  reviewed_by uuid references public.profiles(id) on delete set null,
  title text not null,
  description text not null,
  priority text not null check (priority in ('low', 'medium', 'high', 'urgent')),
  status text not null check (status in ('draft', 'review', 'approved', 'scheduled', 'completed', 'cancelled')),
  ai_recommendation jsonb not null default '{}'::jsonb,
  due_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.rag_queries (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid references public.plants(id) on delete cascade,
  created_by uuid references public.profiles(id) on delete set null,
  query text not null,
  answer text,
  citations jsonb not null default '[]'::jsonb,
  model_used text,
  fallback_used boolean not null default false,
  latency_ms integer check (latency_ms is null or latency_ms >= 0),
  created_at timestamptz not null default now()
);

create table public.model_predictions (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid not null references public.plants(id) on delete cascade,
  asset_id uuid not null references public.assets(id) on delete cascade,
  created_by uuid references public.profiles(id) on delete set null,
  model_name text not null,
  model_version text not null,
  risk_score numeric(5, 4) not null check (risk_score >= 0 and risk_score <= 1),
  predicted_label text not null,
  features jsonb not null default '{}'::jsonb,
  explanation jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table public.audit_logs (
  id uuid primary key default extensions.gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  plant_id uuid references public.plants(id) on delete set null,
  created_by uuid references public.profiles(id) on delete set null,
  actor_user_id uuid,
  action text not null,
  entity_type text not null,
  entity_id uuid,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index profiles_user_id_idx on public.profiles(user_id);
create index profiles_org_role_idx on public.profiles(organization_id, role);
create index plants_org_idx on public.plants(organization_id);
create index assets_org_plant_idx on public.assets(organization_id, plant_id);
create index incidents_org_plant_idx on public.incidents(organization_id, plant_id);
create index documents_org_plant_idx on public.documents(organization_id, plant_id);
create index document_chunks_org_plant_idx on public.document_chunks(organization_id, plant_id);
create index work_orders_org_plant_idx on public.work_orders(organization_id, plant_id);
create index rag_queries_org_plant_idx on public.rag_queries(organization_id, plant_id);
create index model_predictions_org_plant_idx on public.model_predictions(organization_id, plant_id);
create index audit_logs_org_plant_idx on public.audit_logs(organization_id, plant_id);

create or replace function app_private.current_profile_id()
returns uuid
language sql
stable
security definer
set search_path = public, auth
as $$
  select p.id
  from public.profiles p
  where p.user_id = (select auth.uid())
    and p.is_active
  limit 1;
$$;

create or replace function app_private.current_organization_id()
returns uuid
language sql
stable
security definer
set search_path = public, auth
as $$
  select p.organization_id
  from public.profiles p
  where p.user_id = (select auth.uid())
    and p.is_active
  limit 1;
$$;

create or replace function app_private.current_role()
returns text
language sql
stable
security definer
set search_path = public, auth
as $$
  select p.role
  from public.profiles p
  where p.user_id = (select auth.uid())
    and p.is_active
  limit 1;
$$;

create or replace function app_private.current_plant_ids()
returns uuid[]
language sql
stable
security definer
set search_path = public, auth
as $$
  select array_remove(array_append(p.assigned_plant_ids, p.plant_id), null)
  from public.profiles p
  where p.user_id = (select auth.uid())
    and p.is_active
  limit 1;
$$;

create or replace function app_private.can_access_org(target_organization_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public, auth
as $$
  select (select auth.uid()) is not null
    and target_organization_id = app_private.current_organization_id();
$$;

create or replace function app_private.can_access_plant(target_organization_id uuid, target_plant_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public, auth
as $$
  select app_private.can_access_org(target_organization_id)
    and (
      app_private.current_role() = 'admin'
      or target_plant_id = any(coalesce(app_private.current_plant_ids(), '{}'::uuid[]))
    );
$$;

create or replace function app_private.can_manage_plant(target_organization_id uuid, target_plant_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public, auth
as $$
  select app_private.can_access_plant(target_organization_id, target_plant_id)
    and app_private.current_role() in ('admin', 'supervisor');
$$;

create or replace function app_private.is_admin_for_org(target_organization_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public, auth
as $$
  select app_private.can_access_org(target_organization_id)
    and app_private.current_role() = 'admin';
$$;

revoke all on all functions in schema app_private from public;
grant usage on schema app_private to authenticated;
grant execute on all functions in schema app_private to authenticated;

alter table public.organizations enable row level security;
alter table public.plants enable row level security;
alter table public.profiles enable row level security;
alter table public.assets enable row level security;
alter table public.incidents enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.work_orders enable row level security;
alter table public.rag_queries enable row level security;
alter table public.model_predictions enable row level security;
alter table public.audit_logs enable row level security;

revoke all on public.organizations from anon;
revoke all on public.plants from anon;
revoke all on public.profiles from anon;
revoke all on public.assets from anon;
revoke all on public.incidents from anon;
revoke all on public.documents from anon;
revoke all on public.document_chunks from anon;
revoke all on public.work_orders from anon;
revoke all on public.rag_queries from anon;
revoke all on public.model_predictions from anon;
revoke all on public.audit_logs from anon;

grant select on public.organizations, public.plants, public.profiles, public.assets, public.incidents, public.documents, public.document_chunks, public.work_orders, public.rag_queries, public.model_predictions, public.audit_logs to authenticated;
grant insert, update on public.incidents, public.rag_queries, public.model_predictions, public.audit_logs to authenticated;
grant insert, update on public.documents, public.document_chunks, public.work_orders to authenticated;
grant insert, update, delete on public.organizations, public.plants, public.profiles, public.assets to authenticated;

create policy "authenticated users read their organization"
on public.organizations
for select
to authenticated
using (app_private.can_access_org(id));

create policy "admins manage their organization"
on public.organizations
for update
to authenticated
using (app_private.is_admin_for_org(id))
with check (app_private.is_admin_for_org(id));

create policy "authenticated users read assigned plants"
on public.plants
for select
to authenticated
using (app_private.can_access_plant(organization_id, id));

create policy "admins manage plants"
on public.plants
for all
to authenticated
using (app_private.is_admin_for_org(organization_id))
with check (app_private.is_admin_for_org(organization_id));

create policy "users read profiles in assigned plant"
on public.profiles
for select
to authenticated
using (
  id = app_private.current_profile_id()
  or app_private.is_admin_for_org(organization_id)
  or (
    organization_id = app_private.current_organization_id()
    and plant_id = any(coalesce(app_private.current_plant_ids(), '{}'::uuid[]))
  )
);

create policy "admins manage profiles"
on public.profiles
for all
to authenticated
using (app_private.is_admin_for_org(organization_id))
with check (app_private.is_admin_for_org(organization_id));

create policy "users read assigned plant assets"
on public.assets
for select
to authenticated
using (app_private.can_access_plant(organization_id, plant_id));

create policy "admins manage assets"
on public.assets
for all
to authenticated
using (app_private.is_admin_for_org(organization_id))
with check (app_private.is_admin_for_org(organization_id));

create policy "users read assigned plant incidents"
on public.incidents
for select
to authenticated
using (app_private.can_access_plant(organization_id, plant_id));

create policy "users create assigned plant incidents"
on public.incidents
for insert
to authenticated
with check (
  app_private.can_access_plant(organization_id, plant_id)
  and created_by = app_private.current_profile_id()
);

create policy "managers update assigned plant incidents"
on public.incidents
for update
to authenticated
using (app_private.can_manage_plant(organization_id, plant_id))
with check (app_private.can_manage_plant(organization_id, plant_id));

create policy "users read assigned plant documents"
on public.documents
for select
to authenticated
using (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_access_plant(organization_id, plant_id))
);

create policy "managers create documents"
on public.documents
for insert
to authenticated
with check (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_manage_plant(organization_id, plant_id))
  and created_by = app_private.current_profile_id()
);

create policy "managers update documents"
on public.documents
for update
to authenticated
using (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_manage_plant(organization_id, plant_id))
)
with check (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_manage_plant(organization_id, plant_id))
);

create policy "users read assigned plant document chunks"
on public.document_chunks
for select
to authenticated
using (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_access_plant(organization_id, plant_id))
);

create policy "managers create document chunks"
on public.document_chunks
for insert
to authenticated
with check (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_manage_plant(organization_id, plant_id))
  and created_by = app_private.current_profile_id()
);

create policy "managers update document chunks"
on public.document_chunks
for update
to authenticated
using (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_manage_plant(organization_id, plant_id))
)
with check (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_manage_plant(organization_id, plant_id))
);

create policy "users read assigned plant work orders"
on public.work_orders
for select
to authenticated
using (app_private.can_access_plant(organization_id, plant_id));

create policy "supervisors create work orders"
on public.work_orders
for insert
to authenticated
with check (
  app_private.can_manage_plant(organization_id, plant_id)
  and created_by = app_private.current_profile_id()
);

create policy "supervisors update work orders"
on public.work_orders
for update
to authenticated
using (app_private.can_manage_plant(organization_id, plant_id))
with check (app_private.can_manage_plant(organization_id, plant_id));

create policy "users read own rag queries"
on public.rag_queries
for select
to authenticated
using (
  app_private.can_access_org(organization_id)
  and created_by = app_private.current_profile_id()
);

create policy "users create rag queries"
on public.rag_queries
for insert
to authenticated
with check (
  app_private.can_access_org(organization_id)
  and (plant_id is null or app_private.can_access_plant(organization_id, plant_id))
  and created_by = app_private.current_profile_id()
);

create policy "users read assigned plant predictions"
on public.model_predictions
for select
to authenticated
using (app_private.can_access_plant(organization_id, plant_id));

create policy "users create assigned plant predictions"
on public.model_predictions
for insert
to authenticated
with check (
  app_private.can_access_plant(organization_id, plant_id)
  and created_by = app_private.current_profile_id()
);

create policy "admins read audit logs"
on public.audit_logs
for select
to authenticated
using (app_private.is_admin_for_org(organization_id));

create policy "authenticated users create audit logs"
on public.audit_logs
for insert
to authenticated
with check (
  app_private.can_access_org(organization_id)
  and created_by = app_private.current_profile_id()
  and actor_user_id = (select auth.uid())
);
