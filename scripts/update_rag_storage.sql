-- 1. Add 'file_url' column to knowledge_base
ALTER TABLE knowledge_base 
ADD COLUMN IF NOT EXISTS file_url TEXT;

-- 2. Update search function to return file_url
DROP FUNCTION IF EXISTS match_documents(vector, double precision, integer);

create or replace function match_documents (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  content text,
  file_url text, -- New Return Column
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    knowledge_base.id,
    knowledge_base.content,
    knowledge_base.file_url, -- Select new column
    1 - (knowledge_base.embedding <=> query_embedding) as similarity
  from knowledge_base
  where 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
end;
$$;
