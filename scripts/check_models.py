import google.generativeai as genai
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

    genai.configure(api_key=key)

    print("--- AVAILABLE GEMINI MODELS ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
               print(f"✅ {m.name}")
    except Exception as e:
        print(f"❌ Error fetching models: {e}")

if __name__ == "__main__":
    list_models()
