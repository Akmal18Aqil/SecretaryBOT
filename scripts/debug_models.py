import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("API Key not found in .env")
else:
    client = genai.Client(api_key=api_key)
    print("Listing available models...")
    try:
        # Pager object
        for m in client.models.list():
            if 'gemini' in m.name:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
