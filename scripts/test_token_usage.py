
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.listener import ListenerAgent
from src.core.config import settings

def test_token_usage():
    print("🚀 Testing Token Usage for ListenerAgent...")
    print("------------------------------------------")
    
    agent = ListenerAgent(api_key=settings.GOOGLE_API_KEY)
    
    # Test Input
    test_input = "Buatkan surat undangan rapat evaluasi besok jam 8 pagi di studio"
    print(f"📥 Input: '{test_input}'")
    
    # Process
    print("\n⏳ Processing (Check logs below)...\n")
    result = agent.process_request(test_input)
    
    print("\n------------------------------------------")
    if result:
        print("✅ Result received.")
    else:
        print("❌ Failed.")

if __name__ == "__main__":
    test_token_usage()
