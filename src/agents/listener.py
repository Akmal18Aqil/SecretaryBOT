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
            CTX: Now={current_time}. History={history_str}
            TASK: Analyze Input vs History. If follow-up, UPDATE History. If new, IGNORE History.
            OUTPUT: JSON only.
            Ref:
            - CHAT: {{ "intent_type": "CHAT", "reply": "str" }}
            - RECAP: {{ "intent_type": "RECAP" }}
            - ASK: {{ "intent_type": "ASK", "query": "str" }}
            - WORK: {{ "intent_type": "WORK", "jenis_surat": "str", "data": {{...}} }}
            Schemas:
            - `undangan_internal`: [nomor_surat, penerima, acara, hari_tanggal, waktu, tempat]
            - `peminjaman_barang`: [nomor_surat, pemohon, keperluan, nama_barang, waktu_pinjam]
            - `notulensi`: [hari_tanggal, waktu, tempat, agenda, pembahasan, kesimpulan, tugas]
            """ 
            
            # FIX: Do NOT include system_instruction in prompt_parts (Double Entry Error)
            prompt_parts = []
            
            # Handle Audio
            if audio_path and os.path.exists(audio_path):
                logger.info(f"Uploading audio to Gemini: {audio_path}")
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
                
                # Input Audio as Part
                prompt_parts.append(types.Part.from_bytes(data=audio_data, mime_type="audio/ogg"))
                prompt_parts.append("Transkrip & Ekstrak JSON.")
            
            # Input Text
            prompt_parts.append(f"In: {user_input}\nOut JSON:") 

            # Config: ZERO TEMP + JSON MODE (Eliminate Thinking Tax)
            config = types.GenerateContentConfig(
                temperature=0.0, 
                top_p=0.95,
                response_mime_type="application/json",
                system_instruction=system_instruction,
                tools=None 
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_parts,
                config=config
            )
            
            # Log Token Usage (Full Debug)
            if response.usage_metadata:
                usage = response.usage_metadata
                logger.info(f"💰 Token Usage: {usage}")
            
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            logger.info(f"JSON Generated:\n{clean_json}")
            
            # Validate JSON
            json.loads(clean_json) # Check if valid
            
            logger.info("Selesai memproses.")
            return clean_json
            
        except Exception as e:
            logger.error(f"Agent 1 Gagal: {e}")
            return None
