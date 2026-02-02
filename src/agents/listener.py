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

    def process_request(self, user_input, history_context=None, audio_path=None):
        logger.info(f"Mendengar permintaan: '{user_input}' (Audio: {bool(audio_path)})...")
        
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
            
            # History String Formatting
            history_str = "None"
            if history_context:
                history_str = f"PREVIOUS_JSON_STATE: {history_context}"

            system_instruction = f"""
            **Context:** Now={current_time}.
            
            **History (Previous State):**
            {history_str}

            **Task:** 
            1. Analyze **Input** relative to **History**.
            2. If **Input** is a follow-up (e.g., adds detail like time/place), UPDATE the **History** JSON.
            3. If **Input** is a new request, IGNORE history and create new JSON.
            4. Classify intent and extract entities.

            **Intents:**
            1. **CHAT**: Casual/Greeting.
               Output: {{ "intent_type": "CHAT", "reply": "Polite response" }}
            2. **RECAP**: Reports/Logs.
               Output: {{ "intent_type": "RECAP" }}
            3. **ASK**: Q&A/Knowledge.
               Output: {{ "intent_type": "ASK", "query": "Optimized query" }}
            4. **WORK**: Document drafting.
               Rules: Calculate dates relative to Now. Merge with History if related.
               Schemas:
                 - `undangan_internal`: [nomor_surat, penerima, acara, hari_tanggal, waktu, tempat]
                 - `peminjaman_barang`: [nomor_surat, pemohon, keperluan, nama_barang, waktu_pinjam]
               Output: {{ "intent_type": "WORK", "jenis_surat": "...", "data": {{...}} }}

            **Input:** "{user_input}"
            **Output:** JSON only.
            """ 
            
            prompt_parts = [system_instruction]
            
            # Handle Audio
            if audio_path and os.path.exists(audio_path):
                logger.info(f"Uploading audio to Gemini: {audio_path}")
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
                
                # Input Audio as Part
                prompt_parts.append(types.Part.from_bytes(data=audio_data, mime_type="audio/ogg"))
                prompt_parts.append("Transkripsikan audio ini dan ekstrak intent sesuai instruksi JSON di atas.")
            
            # Input Text
            prompt_parts.append(f"Input Text: {user_input}\nOutput JSON:") 

            # Config: LOW TEMP for Logic/Classification
            # Explicitly disable tools to prevent "Phantom Token" usage
            config = types.GenerateContentConfig(
                temperature=0.1, 
                top_p=0.95,
                system_instruction=system_instruction,
                tools=None # Explicitly None to prevent Phantom Tokens
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_parts,
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
