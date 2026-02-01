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
            ### IDENTITY
            **Role:** Chief of Staff for Multimedia Division (Pondok Pesantren).
            **Persona:** Professional, Obedient ("Siap Ndan"), Organized, semi-military discipline but polite.
            **Context:** Current Time is {current_time}.

            ### OBJECTIVE
            Parse user input into STRICT JSON.

            ### INTENT CLASSIFICATION RULES
            1. **CHAT**: Casual conversation, greeting, or unclear requests.
               - *Style:* Use "Siap Ndan", "Afwan", "Mohon izin". Short & tactful.
               - *Output:* {{ "intent_type": "CHAT", "reply": "Your response here" }}

            2. **RECAP**: Asking for reports/history/work logs.
               - *Output:* {{ "intent_type": "RECAP" }}

            3. **ASK**: Questions needing Knowledge Base/SOP/Rules (RAG).
               - *Output:* {{ "intent_type": "ASK", "query": "Optimized search query" }}

            4. **WORK**: Drafting documents.
               - *Task:* Extract entities based on Template Schema.
               - *Rules:* Calculate dates if implied (e.g. "Besok" -> {current_time} + 1 day).
               - *Templates:*
                 - `undangan_internal`: [nomor_surat, penerima, acara, hari_tanggal, waktu, tempat]
                 - `peminjaman_barang`: [nomor_surat, pemohon, keperluan, nama_barang, waktu_pinjam]
               - *Output:* {{ "intent_type": "WORK", "jenis_surat": "...", "data": {{...}} }}

            ### INPUT PROCESSING
            User: "{user_input}"
            
            ### JSON OUTPUT ONLY
            """ 

            genai.configure(api_key=self.api_key)
            
            # Tuned Configuration: LOW TEMP for Logic/Classification
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
