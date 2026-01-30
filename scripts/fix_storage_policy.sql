-- SIMPLIFIED STORAGE POLICY
-- No ALTER TABLE needed (usually enabled by default).

-- 1. Drop old policies to avoid duplicates
DROP POLICY IF EXISTS "Public Upload office_docs" ON storage.objects;
DROP POLICY IF EXISTS "Public Select office_docs" ON storage.objects;

-- 2. Create Upload Policy (ALLOW INSERT)
CREATE POLICY "Public Upload office_docs"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'office_docs');

-- 3. Create Select Policy (ALLOW DOWNLOAD)
CREATE POLICY "Public Select office_docs"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'office_docs');

-- 4. Create Update Policy (ALLOW OVERWRITE)
CREATE POLICY "Public Update office_docs"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'office_docs');
