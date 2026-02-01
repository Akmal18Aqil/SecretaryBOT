import os
import json
from google import genai
from google.genai import types
from datetime import datetime
from src.core.logger import get_logger

logger = get_logger("agent.listener")

class ListenerAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Initialize Client
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def process_request(self, user_input):
        logger.info(f"Mendengar permintaan: '{user_input}'...")
        
        if not self.client:
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
            **Context:** Now={current_time}.
            **Task:** Classify intent and extract entities into JSON.

            **Intents:**
            1. **CHAT**: Casual/Greeting.
               Output: {{ "intent_type": "CHAT", "reply": "Polite response (Siap Ndan)" }}
            2. **RECAP**: Reports/Logs.
               Output: {{ "intent_type": "RECAP" }}
            3. **ASK**: Q&A/Knowledge.
               Output: {{ "intent_type": "ASK", "query": "Optimized query" }}
            4. **WORK**: Document drafting.
               Rules: Calculate dates relative to Now.
               Schemas:
                 - `undangan_internal`: [nomor_surat, penerima, acara, hari_tanggal, waktu, tempat]
                 - `peminjaman_barang`: [nomor_surat, pemohon, keperluan, nama_barang, waktu_pinjam]
               Output: {{ "intent_type": "WORK", "jenis_surat": "...", "data": {{...}} }}

            **Input:** "{user_input}"
            **Output:** JSON only.
            """ 

            # Config: LOW TEMP for Logic/Classification
            # Explicitly disable tools to prevent "Phantom Token" usage
            config = types.GenerateContentConfig(
                temperature=0.1, 
                top_p=0.95,
                system_instruction=system_instruction,
                tools=[], # Removing this just in case
                tool_config={'function_calling_config': {'mode': 'NONE'}}            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Input: {user_input}\nOutput JSON:",
                config=config
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
