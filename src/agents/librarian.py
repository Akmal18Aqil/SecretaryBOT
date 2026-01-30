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

        # 3. Construct Context
        context_text = "\n---\n".join([f"{d['content']}" for d in docs])
        logger.info(f"Found {len(docs)} documents.")

        # 4. Generate Answer using LLM
        prompt = f"""
        YOU ARE 'THE SECRETARY SWARM':
        A helpful, witty, and professional AI Assistant for a Pesantren Multimedia Team.
        
        YOUR TASK:
        Answer the USER QUESTION based on the provided CONTEXT.

        CONTEXT (KNOWLEDGE BASE):
        {context_text}

        USER QUESTION:
        {user_query}

        INSTRUCTIONS:
        1. **Be Helpful**: Explain the answer clearly.
        2. **Be Witty**: Use a slightly casual, respectful Indonesian tone (ala 'Santri Modern').
        3. **Don't be Robot**: Avoid phrases like "Berdasarkan konteks". Just answer directly.
        4. **If Uncertain**: If the context mentions the TOPIC but lacks DETAILS, say what you found and admit what is missing politely.
           (e.g., "Saya nemu judul SOP-nya, tapi detail isinya belum ada di database saya, Bos.")
        5. **No Hallucinations**: Only use facts from the Context.
        """
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Answer Gen Error: {e}")
            return "Maaf, saya gagal merangkum jawaban."
