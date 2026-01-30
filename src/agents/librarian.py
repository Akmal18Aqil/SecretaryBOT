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
        You are the 'Senior Archivist' of the Multimedia Team.
        You hold all the knowledge (SOPs, Guidelines, Rules).
        
        YOUR TRAITS:
        1. **Authoritative**: You know the rules better than anyone.
        2. **Helpful but Brief**: Give the answer directly. Don't waffle.
        3. **Structured**: Use bullet points or bold text for key info.
        
        TASK:
        Answer the User's Question based ONLY on the Context provided below.
        
        ---
        CONTEXT FROM ARCHIVE:
        {context_text}
        
        AVAILABLE FILES:
        {files_text}
        
        USER QUESTION:
        {user_query}
        ---
        
        GUIDELINES:
        - Jika jawaban ada di konteks: Jawab dengan tegas. "Berdasarkan SOP No. X..."
        - Jika ada file terkait: "Cek detailnya di dokumen ini: [SOP Link]" sent only if url matches available files.
        - Jika TIDAK ada di konteks: "Wah, data itu belum ada di arsip saya, Ndan. Coba cek manual atau tanya Ketua." (Jangan mengarang!).
        - Sapaan: Gunakan "Ndan" (Komandan) atau "Tadz" (Ustadz) sesekali untuk bonding.
        """
        
        try:
            # Tuned for RAG: Low Hallucination but Natural Flow
            generation_config = genai.types.GenerationConfig(
                temperature=0.4,
                top_p=0.85,
            )
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Answer Gen Error: {e}")
            return "Maaf, saya gagal merangkum jawaban."
