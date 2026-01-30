import sys
import os
import time
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document as DocxReader
from PIL import Image
from google.api_core.exceptions import ResourceExhausted

# Add root project to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import settings
from src.core.database import db

# Init Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(path):
    doc = DocxReader(path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_text_from_image(path):
    """
    Use Gemini Vision to describe the image/flowchart.
    """
    print("👀 Vision AI is looking at the image...")
    img = Image.open(path)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    retry_count = 0
    while retry_count < 3:
        try:
            response = model.generate_content([
                "Transcribe this Flowchart/Diagram into a detailed Step-by-Step SOP text in Indonesian. Don't miss any decision points.", 
                img
            ])
            return response.text
        except ResourceExhausted:
            print("⏳ Quota Limit reached. Cooling down 60s... (Please Wait)")
            time.sleep(60)
            retry_count += 1
        except Exception as e:
            print(f"❌ Vision Error: {e}")
            return ""
    
    print("❌ Failed after retries.")
    return ""

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Split long text into chunks for better vector search.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap) # Geser window dengan overlap
    
    return chunks

def get_embedding(text):
    """
    Generate vector (768 dim) for text using Gemini.
    """
    retry_count = 0
    while retry_count < 3:
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
                title="Knowledge Base"
            )
            return result['embedding']
        except ResourceExhausted:
            print("⏳ Embed Quota reached. Cooling down 30s...")
            time.sleep(30)
            retry_count += 1
        except Exception as e:
            print(f"⚠️ Vector Error: {e}")
            return None
    return None

def process_input(input_data):
    # Check if input is a file path
    if os.path.isfile(input_data):
        print(f"📂 Detected File: {input_data}")
        ext = input_data.split('.')[-1].lower()
        
        if ext == 'pdf':
            raw_text = extract_text_from_pdf(input_data)
        elif ext in ['docx', 'doc']:
            raw_text = extract_text_from_docx(input_data)
        elif ext in ['png', 'jpg', 'jpeg', 'webp']:
            raw_text = extract_text_from_image(input_data)
            if not raw_text:
                print("❌ Failed to read text from image.")
                return
        elif ext == 'txt':
            with open(input_data, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        else:
            print("❌ Unsupported file format. Use PDF, DOCX, IMG, or TXT.")
            return
    else:
        # Assume direct text input
        print("📝 Detected Text Input.")
        raw_text = input_data

    # Chunking
    chunks = chunk_text(raw_text)
    print(f"✂️  Split into {len(chunks)} chunks.")

    # Process each chunk
    client = db.get_client()
    
    # 1. Upload File to Storage (If input is a file)
    file_url = None
    if os.path.isfile(input_data):
        file_name = os.path.basename(input_data)
        try:
            with open(input_data, 'rb') as f:
                print(f"☁️ Uploading {file_name} to Supabase Storage...")
                # Upload to 'office_docs' bucket
                res = client.storage.from_("office_docs").upload(
                    file=f,
                    path=file_name,
                    file_options={"upsert": "true"}
                )
                # Get Public URL
                file_url = client.storage.from_("office_docs").get_public_url(file_name)
                print(f"🔗 File Public URL: {file_url}")
        except Exception as e:
            print(f"⚠️ Storage Upload Error: {e}")

    # 2. Insert Chunks with URL
    for i, chunk in enumerate(chunks, 1):
        if len(chunk.strip()) < 10: continue # Skip empty chunks
        
        print(f"   🔹 Processing Chunk {i}/{len(chunks)}...", end="\r")
        vector = get_embedding(chunk)
        
        if vector:
            data = {
                "content": chunk, 
                "embedding": vector,
                "file_url": file_url # Save the link!
            }
            try:
                client.table('knowledge_base').insert(data).execute()
            except Exception as e:
                print(f"\n❌ DB Error: {e}")

    print("\n✅ All chunks uploaded to Knowledge Base!")

if __name__ == "__main__":
    print("--- ADMIN: KNOWLEDGE UPLOADER ---")
    print("Supports: Manual Text, PDF, DOCX, TXT")
    print("Now Supports: IMAGES/DIAGRAMS (PNG, JPG) 📸")
    print("Type 'EXIT' to quit.")
    print("-----------------------------------")
    
    while True:
        user_input = input("\nMasukkan Teks / Path File (ex: C:\\docs\\diagram.png): ")
        
        # Remove quotation marks if user dragged file
        user_input = user_input.strip('"') 
        
        if user_input.strip().upper() == 'EXIT':
            break
            
        if len(user_input.strip()) == 0: continue
            
        # Handle case where user drags file with spaces in path
        if os.path.exists(user_input):
             process_input(user_input)
        else:
             # Fallback for text
             process_input(user_input)
