from google import genai
import os
import sys

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.core.config import settings

def list_models():
    key = settings.GOOGLE_API_KEY
    if not key:
        print("❌ Script Error: APK Key not found in .env")
        return

    client = genai.Client(api_key=key)

    print("--- AVAILABLE GEMINI MODELS ---")
    try:
        # Pager object, iterate to find models
        for m in client.models.list():
            # Check naming convention for Gemini models
            if "gemini" in m.name:
               print(f"✅ {m.name}")
    except Exception as e:
        print(f"❌ Error fetching models: {e}")

if __name__ == "__main__":
    list_models()
