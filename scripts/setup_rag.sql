-- 1. Enable Vector Extension (Wajib untuk RAG)
create extension if not exists vector;

-- 2. Create Table KNOWLEDGE_BASE
create table knowledge_base (
  id uuid default uuid_generate_v4() primary key,
  content text not null,                -- Isi SOP / Data
  embedding vector(768),                -- Vektor dari Gemini (768 dimensi)
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. Enable RLS (Opsional, matikan dulu biar mudah)
alter table knowledge_base enable row level security;
create policy "Public Read Access" on knowledge_base for select using (true);
create policy "Admin Insert Access" on knowledge_base for insert with check (true);

-- 4. Create Search Function (RPC)
-- Fungsi ini akan dipanggil oleh Bot untuk mencari data mirip
create or replace function match_documents (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  content text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    knowledge_base.id,
    knowledge_base.content,
    1 - (knowledge_base.embedding <=> query_embedding) as similarity
  from knowledge_base
  where 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
end;
$$;
