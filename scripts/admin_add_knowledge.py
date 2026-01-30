import sys
import os
import google.generativeai as genai

# Add root project to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import settings
from src.core.database import db

# Init Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

def get_embedding(text):
    """
    Generate vector (768 dim) for text using Gemini.
    """
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",
        title="Knowledge Base"
    )
    return result['embedding']

def upload_knowledge(text):
    print(f"Processing: {text[:50]}...")
    
    # 1. Get Embedding
    try:
        vector = get_embedding(text)
        print("✅ Vector Generated")
    except Exception as e:
        print(f"❌ Failed to generate vector: {e}")
        return

    # 2. Upload to Supabase
    try:
        data = {
            "content": text,
            "embedding": vector
        }
        db.get_client().table('knowledge_base').insert(data).execute()
        print("✅ Success! Data saved to Knowledge Base.")
    except Exception as e:
        print(f"❌ Failed to upload to DB: {e}")

if __name__ == "__main__":
    print("--- ADMIN: ADD KNOWLEDGE ---")
    print("Tools ini akan menyimpan data ke Otak Bot (Supabase Vector).")
    print("Tulis SOP/Info yang ingin Anda ajarkan (Ketik 'EXIT' untuk selesai).")
    print("----------------------------")
    
    while True:
        user_input = input("\nMasukkan Info/SOP: ")
        if user_input.strip().upper() == 'EXIT':
            break
            
        if len(user_input) < 10:
            print("❌ Terlalu pendek. Minimal 1 kalimat lengkap.")
            continue
            
        upload_knowledge(user_input)
