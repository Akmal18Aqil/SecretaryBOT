import os
import json
import google.generativeai as genai

class ListenerAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.system_instruction = """
        You are 'The Listener', an intelligent administrative assistant for a Pesantren. 
        Your goal is to extract structured data from informal requests into a JSON format used for document generation.

        RULES:
        1. Always output strictly valid JSON.
        2. Identify the 'intent' (jenis_surat) based on keywords.
           - Peminjaman Barang -> 'peminjaman_barang'
           - Undangan Rapat -> 'undangan_internal'
           - Surat Tugas -> 'surat_tugas'
        3. Convert relative dates (besok, lusa) into specific dates (Format: DD MMMM YYYY, Bahasa Indonesia).
        4. JSON keys must match the template placeholders.
        5. CRITICAL: If the request is too vague, unclear, or missing essential details (like 'who', 'what', 'when'), DO NOT GUESS. Instead, return a JSON with an "error" key explaining what is missing in polite Indonesian.
           Example Error JSON: 
           {
             "error": "Mohon maaf, instruksi Anda kurang spesifik. Saya perlu tahu jenis suratnya (Undangan/Peminjaman) dan detail isinya.", 
             "missing_info": "Jenis surat, Tujuan, Tanggal"
           }
        """

    def process_request(self, user_input):
        print(f"\n[Agent 1] Mendengar permintaan: '{user_input}'...")
        
        if not self.api_key:
            print("[INFO] API Key tidak ditemukan. Menggunakan MOCK MODE (Simulasi AI).")
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
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=self.system_instruction)
            response = model.generate_content(f"Input: {user_input}\nOutput JSON:")
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            print(f"[DEBUG AGENT 1] JSON Generated:\n{clean_json}\n-------------------")
            # Validate JSON
            json.loads(clean_json) # Check if valid
            print("[Agent 1] Selesai memproses.")
            return clean_json
        except Exception as e:
            print(f"[ERROR] Agent 1 Gagal: {e}")
            return None
