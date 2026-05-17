alter table public.assets
  drop constraint if exists assets_status_check;

alter table public.assets
  add constraint assets_status_check
  check (status in ('healthy', 'watch', 'high_risk', 'degraded', 'critical', 'offline'));

alter table public.work_orders
  drop constraint if exists work_orders_status_check;

alter table public.work_orders
  add constraint work_orders_status_check
  check (status in ('draft', 'review', 'approved', 'assigned', 'closed', 'scheduled', 'completed', 'cancelled'));

create or replace function public.match_document_chunks(
  query_embedding extensions.vector(768),
  match_count integer,
  filter_organization_id uuid,
  filter_plant_id uuid
)
returns table (
  chunk_id uuid,
  document_id uuid,
  title text,
  content text,
  source_uri text,
  source_page integer,
  similarity double precision
)
language sql
stable
security invoker
set search_path = public, extensions
as $$
  with scoped_chunks as (
    select
      dc.id,
      dc.document_id,
      dc.title,
      dc.content,
      dc.source_uri,
      dc.source_page,
      dc.embedding
    from public.document_chunks dc
    where dc.organization_id = filter_organization_id
      and (filter_plant_id is null or dc.plant_id = filter_plant_id)
  ),
  scored_chunks as (
    select
      sc.id,
      sc.document_id,
      sc.title,
      sc.content,
      sc.source_uri,
      sc.source_page,
      case
        when sc.embedding is null then 0.01::double precision
        else 1 - (sc.embedding <=> query_embedding)
      end as similarity
    from scoped_chunks sc
  )
  select
    scored_chunks.id,
    scored_chunks.document_id,
    scored_chunks.title,
    scored_chunks.content,
    scored_chunks.source_uri,
    scored_chunks.source_page,
    scored_chunks.similarity
  from scored_chunks
  order by scored_chunks.similarity desc
  limit least(greatest(match_count, 1), 10);
$$;

revoke all on function public.match_document_chunks(extensions.vector, integer, uuid, uuid) from anon;
grant execute on function public.match_document_chunks(extensions.vector, integer, uuid, uuid) to authenticated;

create or replace function app_private.can_access_storage_object(object_name text)
returns boolean
language sql
stable
security definer
set search_path = public, storage
as $$
  select app_private.current_organization_id() is not null
    and split_part(object_name, '/', 1) = app_private.current_organization_id()::text
    and (
      app_private.current_role() = 'admin'
      or split_part(object_name, '/', 2) = any(
        array(select unnest(coalesce(app_private.current_plant_ids(), '{}'::uuid[]))::text)
      )
    );
$$;

create or replace function app_private.can_manage_storage_object(object_name text, allowed_roles text[])
returns boolean
language sql
stable
security definer
set search_path = public, storage
as $$
  select app_private.can_access_storage_object(object_name)
    and app_private.current_role() = any(allowed_roles);
$$;

revoke all on function app_private.can_access_storage_object(text) from public;
revoke all on function app_private.can_manage_storage_object(text, text[]) from public;
grant execute on function app_private.can_access_storage_object(text) to authenticated;
grant execute on function app_private.can_manage_storage_object(text, text[]) to authenticated;

drop policy if exists "PlantOps authenticated users can read scoped documents" on storage.objects;
drop policy if exists "PlantOps reliability and supervisors can upload documents" on storage.objects;
drop policy if exists "PlantOps supervisors and admins can update documents" on storage.objects;

create policy "PlantOps authenticated users can read scoped documents"
on storage.objects
for select
to authenticated
using (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and app_private.can_access_storage_object(name)
);

create policy "PlantOps reliability and supervisors can upload scoped documents"
on storage.objects
for insert
to authenticated
with check (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and app_private.can_manage_storage_object(name, array['reliability_engineer', 'supervisor', 'admin'])
);

create policy "PlantOps supervisors and admins can update scoped documents"
on storage.objects
for update
to authenticated
using (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and app_private.can_manage_storage_object(name, array['supervisor', 'admin'])
)
with check (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and app_private.can_manage_storage_object(name, array['supervisor', 'admin'])
);
