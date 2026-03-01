import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=key)

text = "Testing dimension"
result = client.models.embed_content(
    model="models/gemini-embedding-001",
    contents=text,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
)
print(f"Dimensions: {len(result.embeddings[0].values)}")
