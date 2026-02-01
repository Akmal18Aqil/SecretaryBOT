from google import genai
from google.genai import types
from src.core.database import db
from src.core.logger import get_logger

logger = get_logger("agent.librarian")

class LibrarianAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.db = db

    def get_embedding(self, text):
        """
        Generate vector for query.
        """
        try:
            result = self.client.models.embed_content(
                model="models/text-embedding-004",
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding Gen Error: {e}")
            return None

    def answer_question(self, user_query):
        """
        Main RAG Workflow: Query -> Vector -> Search DB -> Generate Answer
        """
        logger.info(f"Librarian searching for: {user_query}")
        
        # 1. Generate Vector
        query_vector = self.get_embedding(user_query)
        if not query_vector:
            return "Maaf, sistem pencarian sedang gangguan (Embedding Error)."

        # 2. Search Database
        # Threshold 0.35 agar lebih banyak konteks yang masuk
        docs = self.db.search_knowledge(query_vector, match_threshold=0.35, match_count=3)
        
        if not docs:
            return "Maaf, Bos. Saya sudah cari di tumpukan dokumen tapi gak nemu info soal itu. 🙏"

        # 3. Construct Context with File URLs
        context_parts = []
        file_urls = set()
        
        for d in docs:
            content = d.get('content', '')
            url = d.get('file_url')
            
            context_parts.append(content)
            if url:
                file_urls.add(url)

        context_text = "\n---\n".join(context_parts)
        files_text = "\n".join([f"- {u}" for u in file_urls]) if file_urls else "No files available."

        logger.info(f"Found {len(docs)} docs. Files found: {list(file_urls)}")

        # 4. Generate Answer using LLM
        prompt = f"""
        **Role:** Assistant (Polite "Siap Ndan").
        **Task:** Answer using provided CONTEXT only.

        [CONTEXT]
        {context_text}

        [FILES]
        {files_text}

        [QUERY]
        "{user_query}"

        **Rules:**
        1. **Info**: Summarize CONTEXT.
        2. **File**: If user asks download/file, provide URL from [FILES].
        3. **Style**: Direct, bullet points, polite.
        4. **Safety**: NO markdown on URLs. NO hallucination.
        """
        
        try:
            # Tuned for RAG: Balanced Creativity (0.3)
            config = types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.85,
            )
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )
            
            # Log Token Usage
            if response.usage_metadata:
                usage = response.usage_metadata
                logger.info(f"💰 Token Usage [Librarian]: Input={usage.prompt_token_count}, Output={usage.candidates_token_count}, Total={usage.total_token_count}")

            return response.text.strip()
        except Exception as e:
            logger.error(f"Answer Gen Error: {e}")
            return "Maaf, saya gagal merangkum jawaban."
