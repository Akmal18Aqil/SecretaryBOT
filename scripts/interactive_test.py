import sys
import os

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.librarian import LibrarianAgent
from src.core.config import settings

def interactive_test():
    print("--- INTERACTIVE LIBRARIAN TEST ---")
    
    key = settings.GOOGLE_API_KEY
    if not key:
        print("❌ GOOGLE_API_KEY missing in .env")
        return

    agent = LibrarianAgent(api_key=key)
    print("✅ LibrarianAgent Ready. Type 'exit' to quit.\n")

    while True:
        query = input("You: ")
        if query.lower() in ['exit', 'quit']:
            break
            
        print("Bot: Thinking...", end="\r")
        answer = agent.answer_question(query)
        print(f"Bot: {answer}\n")
        print("-" * 50)

if __name__ == "__main__":
    interactive_test()
