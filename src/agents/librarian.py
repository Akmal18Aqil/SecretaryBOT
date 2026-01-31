import google.generativeai as genai
from src.core.database import db
from src.core.logger import get_logger

logger = get_logger("agent.librarian")

class LibrarianAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.db = db

    def get_embedding(self, text):
        """
        Generate vector for query.
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
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
        docs = self.db.search_knowledge(query_vector, match_threshold=0.35, match_count=5)
        
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

        logger.info(f"Found {len(docs)} docs, {len(file_urls)} files.")

        # 4. Generate Answer using LLM
        prompt = f"""
        IDENTITY:
        You are the 'Multimedia Division Secretary & Knowledge Guardian'.
        You manage ALL knowledge for the team: SOPs, Guidelines, Member Data, Inventories, and Histories.
        
        YOUR TRAITS:
        1. **Smart & Adaptable**: You can answer formal SOP questions OR casual data questions (e.g., "Siapa yang bisa desain?").
        2. **Helpful & Direct**: Give the answer directly.
        3. **Structured**: Use lists/bullet points for data.
        
        TASK:
        Answer the User's Question based ONLY on the Context provided below.
        
        ---
        CONTEXT FROM KNOWLEDGE BASE:
        {context_text}
        
        AVAILABLE FILES:
        {files_text}
        
        USER QUESTION:
        {user_query}
        ---
        
        GUIDELINES:
        GUIDELINES:
        - **Analyze the Question Type**:
          - IF asking for Explanation/Info (e.g., "Apa itu...", "Bagaimana alur..."): Focus on the ANSWER. Do NOT provide file links.
          - IF asking for Data (People/Inventory): Extract the list.
          - IF AND ONLY IF asking for the File/Download (e.g., "minta file", "bagi link", "download"): Provide the link from 'AVAILABLE FILES'.
        - **STRICT RULE**: If the user does NOT use words like "file", "link", or "download", DO NOT include the URL. Just answer the question based on text.
        - Jika TIDAK ada di konteks: "Data tersebut tidak ditemukan di arsip file yang saya baca, Ndan."
        - Sapaan: Gunakan "Ndan" atau "Tadz".
        """
        
        try:
            # Tuned for RAG: Low Hallucination but Natural Flow
            generation_config = genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.85,
            )
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Log Token Usage
            if response.usage_metadata:
                usage = response.usage_metadata
                logger.info(f"💰 Token Usage [Librarian]: Input={usage.prompt_token_count}, Output={usage.candidates_token_count}, Total={usage.total_token_count}")

            return response.text.strip()
        except Exception as e:
            logger.error(f"Answer Gen Error: {e}")
            return "Maaf, saya gagal merangkum jawaban."
