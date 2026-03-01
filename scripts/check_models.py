from google import genai
import os
import sys

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.config import settings

def list_models():
    key = settings.GOOGLE_API_KEY
    if not key:
        print("❌ Script Error: APK Key not found in .env")
        return

    client = genai.Client(api_key=key)

    print("--- ALL AVAILABLE MODELS ---")
    try:
        with open("models_list.txt", "w") as f:
            for m in client.models.list():
                f.write(f"{m.name}\n")
        print("✅ Models written to models_list.txt")
    except Exception as e:
        print(f"❌ Error fetching models: {e}")

if __name__ == "__main__":
    list_models()
