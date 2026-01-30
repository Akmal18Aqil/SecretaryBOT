import os
import json
import google.generativeai as genai
from datetime import datetime
from src.core.logger import get_logger

logger = get_logger("agent.listener")

class ListenerAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Prompt is now dynamic in process_request

    def process_request(self, user_input):
        logger.info(f"Mendengar permintaan: '{user_input}'...")
        
        if not self.api_key:
            logger.warning("API Key tidak ditemukan. Menggunakan MOCK MODE (Simulasi AI).")
            # Simulasi output AI pintar
            return json.dumps({
                "jenis_surat": "undangan_internal",
                "data": {
                    "nomor_surat": "007/SANTRI-MM/I/2026",
                    "penerima": "Ust. Abdurrahman",
                    "hari_tanggal": "Jumat, 30 Januari 2026",
                    "waktu": "20.00 WIB - Selesai",
                    "tempat": "Studio Multimedia",
                    "acara": "Rapat Evaluasi Bulanan & Makan Bersama",
                }
            })

        try:
            # Dynamic Context
            current_time = datetime.now().strftime("%A, %d %B %Y, Jam %H:%M")
            
            system_instruction = f"""
            ROLE:
            You are 'The Secretary', the Chief of Staff for the Multimedia Team. 
            You are EFFICIENT, SLIGHTLY BOSSY, and HIGHLY ORGANIZED.

            CONTEXT:
            Current Time: {current_time}

            YOUR JOB:
            Analyze the user's input and extract structured data into JSON.

            STYLE GUIDE (FOR 'CHAT' REPLY):
            - Tone: Profesional, direct, but respectful (khas lingkungan Pesantren).
            - Keywords: "Siap Ndan", "Afwan", "Segera diproses", "Data tidak lengkap".
            - Don't be too chatty. Get to work.

            ---
            ### VALID INTENTS:

            1. **CHAT** (Small talk, greetings, unrelated questions)
               Output: {{ "intent_type": "CHAT", "reply": "Respon kamu disini..." }}

            2. **RECAP** (Asking for history, logs, reports)
               Output: {{ "intent_type": "RECAP" }}

            3. **ASK** (Asking for SOP, Knowledge, Guidelines - RAG)
               Output: {{ "intent_type": "ASK", "query": "Refined search query" }}

            4. **WORK** (Drafting specific documents)
               Output: {{ 
                   "intent_type": "WORK", 
                   "jenis_surat": "nama_template", 
                   "data": {{ ...extracted_fields... }} 
               }}

            ---
            ### WORK SCHEMA (TEMPLATE RULES):

            **Rule:** If specific data (like date/time) is implied (e.g., "besok", "nanti malam"), CALCULATE IT based on Current Time.

            **A. Undangan Internal ('undangan_internal')**
            Fields: nomor_surat, penerima, acara, hari_tanggal, waktu, tempat.
            *Default Tempat:* "Kantor Studio Multimedia"

            **B. Peminjaman Barang ('peminjaman_barang')**
            Fields: nomor_surat, pemohon, keperluan, nama_barang, waktu_pinjam.

            ---
            INPUT: "{user_input}"
            OUTPUT JSON ONLY:
            """

            genai.configure(api_key=self.api_key)
            
            # Use specific generation config for consistency
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.95,
            )
            
            model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)
            
            response = model.generate_content(
                f"Input: {user_input}\nOutput JSON:",
                generation_config=generation_config
            )
            
            # Log Token Usage
            if response.usage_metadata:
                usage = response.usage_metadata
                logger.info(f"💰 Token Usage [Listener]: Input={usage.prompt_token_count}, Output={usage.candidates_token_count}, Total={usage.total_token_count}")
            
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            logger.info(f"JSON Generated:\n{clean_json}")
            
            # Validate JSON
            json.loads(clean_json) # Check if valid
            
            logger.info("Selesai memproses.")
            return clean_json
            
        except Exception as e:
            logger.error(f"Agent 1 Gagal: {e}")
            return None
