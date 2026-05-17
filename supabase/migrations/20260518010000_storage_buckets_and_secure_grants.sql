insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values
  ('plantops-documents', 'plantops-documents', false, 10485760, array['text/plain', 'text/markdown', 'application/pdf']),
  ('plantops-reports', 'plantops-reports', false, 5242880, array['text/plain', 'text/markdown', 'application/json'])
on conflict (id) do update
set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

create policy "PlantOps authenticated users can read scoped documents"
on storage.objects
for select
to authenticated
using (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and exists (
    select 1
    from public.profiles p
    where p.user_id = (select auth.uid())
      and p.is_active
  )
);

create policy "PlantOps reliability and supervisors can upload documents"
on storage.objects
for insert
to authenticated
with check (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and app_private.current_role() in ('reliability_engineer', 'supervisor', 'admin')
);

create policy "PlantOps supervisors and admins can update documents"
on storage.objects
for update
to authenticated
using (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and app_private.current_role() in ('supervisor', 'admin')
)
with check (
  bucket_id in ('plantops-documents', 'plantops-reports')
  and app_private.current_role() in ('supervisor', 'admin')
);

grant usage on schema public to authenticated;
grant select, insert, update on
  public.incidents,
  public.documents,
  public.document_chunks,
  public.rag_queries,
  public.model_predictions,
  public.work_orders,
  public.audit_logs
to authenticated;

grant select on
  public.organizations,
  public.plants,
  public.profiles,
  public.assets
to authenticated;
