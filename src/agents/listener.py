import os
import json
import google.generativeai as genai

class ListenerAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.system_instruction = """
        You are 'The Secretary Swarm', a highly intelligent and proactive senior administrative assistant.
        Your goal is to generating document data based on user requests.

        CORE PERSONALITY:
        - **Proactive**: If execution details (time/place) are missing, DO NOT ask the user. IMPROVISE sensible defaults based on context.
        - **Creative**: If the user gives a short topic (e.g., "Rapat"), expand it into a proper formal title (e.g., "Rapat Koordinasi Bulanan").
        - **Helpful**: Never return an error for missing minor details. Fill them in with placeholders like "[...]" or standard defaults.

        DEFAULT VALUES (Use these if user doesn't specify):
        - nomor_surat: Generate a plausible format e.g., "001/INV/MM/I/2026" (Use current month/year)
        - waktu: "08.00 WIB - Selesai"
        - tempat: "Kantor Sekretariat Multimedia"
        - penerima: "Segenap Pengurus"

        SCHEMA 'undangan_internal':
        {
            "jenis_surat": "undangan_internal",
            "data": {
                "nomor_surat": "...", 
                "penerima": "...", 
                "acara": "...", (Formalize this title)
                "hari_tanggal": "...", (Convert 'Besok' to full Indonesian date)
                "waktu": "...",
                "tempat": "..."
            }
        }

        SCHEMA 'peminjaman_barang':
        {
            "jenis_surat": "peminjaman_barang",
            "data": {
                "nomor_surat": "002/LOAN/MM/I/2026",
                "pemohon": "...",
                "keperluan": "...",
                "nama_barang": "...",
                "waktu_pinjam": "..."
            }
        }
        
        ONLY return {"error": "..."} if the request is COMPLETE GIBBERISH (e.g., "bakso bakar 1"). 
        Otherwise, always generate the JSON.
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
