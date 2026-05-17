alter table public.document_chunks
  add column if not exists title text,
  add column if not exists source_uri text,
  add column if not exists source_page integer;

update public.document_chunks dc
set
  title = coalesce(dc.title, d.title),
  source_uri = coalesce(dc.source_uri, d.source_uri),
  source_page = coalesce(dc.source_page, dc.page_number)
from public.documents d
where dc.document_id = d.id;

alter table public.document_chunks
  alter column title set not null;

create index if not exists document_chunks_embedding_ivfflat_idx
  on public.document_chunks
  using ivfflat (embedding extensions.vector_cosine_ops)
  with (lists = 64)
  where embedding is not null;

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
  select
    dc.id,
    dc.document_id,
    dc.title,
    dc.content,
    dc.source_uri,
    dc.source_page,
    1 - (dc.embedding <=> query_embedding) as similarity
  from public.document_chunks dc
  where dc.organization_id = filter_organization_id
    and (filter_plant_id is null or dc.plant_id = filter_plant_id)
    and dc.embedding is not null
  order by dc.embedding <=> query_embedding
  limit least(greatest(match_count, 1), 10);
$$;
