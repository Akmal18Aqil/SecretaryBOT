import sys
import os

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.librarian import LibrarianAgent
from src.core.config import settings

def test_rag():
    print("--- DIAGNOSTIC: RAG SYSTEM ---")
    
    # 1. Check Key
    key = settings.GOOGLE_API_KEY
    if not key:
        print("❌ GOOGLE_API_KEY missing in .env")
        return
    print(f"✅ API Key found: {key[:5]}...")

    # 2. Init Agent
    try:
        agent = LibrarianAgent(api_key=key)
        print("✅ LibrarianAgent Initialized")
    except Exception as e:
        print(f"❌ Failed to init agent: {e}")
        return

    # 3. Test Embedding
    query = "SOP perizinan malam"
    print(f"\nTesting Embedding for: '{query}'")
    vector = agent.get_embedding(query)
    if vector:
        print("✅ Embeddings generated successfully")
    else:
        print("❌ Failed to generate embeddings")
        return

    # 4. Test Search
    print("\nTesting Database Search...")
    docs = agent.db.search_knowledge(vector, match_threshold=0.5)
    print(f"Found {len(docs)} documents.")
    for d in docs:
        print(f" - {d['content'][:50]}...")

    # 5. Test Generation (The failing part)
    print("\nTesting Answer Generation (LLM)...")
    try:
        answer = agent.answer_question(query)
        print(f"\n🤖 ANSWER:\n{answer}")
        
        if "Maaf, saya gagal" in answer:
             print("\n❌ LLM Generation Failed (Caught by Try/Except block)")
        else:
             print("\n✅ LLM Generation Success!")
             
    except Exception as e:
        print(f"❌ Crash during generation: {e}")

if __name__ == "__main__":
    test_rag()
