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
        # Threshold 0.5 cukup aman, kalau 0.7 mungkin terlalu ketat
        docs = self.db.search_knowledge(query_vector, match_threshold=0.4, match_count=3)
        
        if not docs:
            return "Maaf, saya belum punya informasi tentang hal itu di database SOP/Kantor. 🙏"

        # 3. Construct Context
        context_text = "\n\n".join([f"- {d['content']}" for d in docs])
        logger.info(f"Found {len(docs)} documents.")

        # 4. Generate Answer using LLM
        prompt = f"""
        CONTEXT (DATA KANTOR/SOP):
        {context_text}

        USER QUESTION:
        {user_query}

        INSTRUCTION:
        Answer the user's question based ONLY on the context above.
        If the context doesn't have the answer, say you don't know (don't hallucinate).
        Use a professional and helpful tone (Indonesian).
        """
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Answer Gen Error: {e}")
            return "Maaf, saya gagal merangkum jawaban."
