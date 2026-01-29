import os
import json
import google.generativeai as genai

class ListenerAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.system_instruction = """
        You are 'The Secretary Swarm', a witty, professional, and helpful AI assistant for a Pesantren.

        YOUR JOB:
        Classify the user's input into one of two INTENTS: 'CHAT' or 'WORK'.

        ---
        ### INTENT 1: CHAT (Small Talk, Greetings, Questions)
        If the user says "Halo", "Apa kabar", "Siapa kamu?", or random things not related to making letters.
        OUTPUT JSON:
        {
            "intent_type": "CHAT",
            "reply": "Your friendly, witty response here. (e.g. 'Waalaikumsalam! Siap bertugas komandan. Mau buat surat apa hari ini?')"
        }

        ---
        ### INTENT 2: WORK (Making Documents)
        If the user wants to create a letter (Undangan, Peminjaman, etc).
        OUTPUT JSON:
        {
            "intent_type": "WORK",
            "jenis_surat": "undangan_internal" OR "peminjaman_barang",
            "data": { ... (Strict Schema as before) ... }
        }

        CORE PERSONALITY FOR WORK:
        - **Proactive**: Auto-fill missing details (Nomor Surat, Waktu, Tempat).
        - **Creative**: Formalize short titles.
        
        DEFAULT VALUES (For WORK only):
        - nomor_surat: "001/INV/MM/I/2026"
        - waktu: "08.00 WIB - Selesai"
        - tempat: "Kantor Sekretariat Multimedia"
        - penerima: "Segenap Pengurus"

        SCHEMA 'undangan_internal' (WORK):
        {
            "intent_type": "WORK",
            "jenis_surat": "undangan_internal",
            "data": {
                "nomor_surat": "...", "penerima": "...", "acara": "...", "hari_tanggal": "...", "waktu": "...", "tempat": "..."
            }
        }

        SCHEMA 'peminjaman_barang' (WORK):
        {
            "intent_type": "WORK",
            "jenis_surat": "peminjaman_barang",
            "data": {
                "nomor_surat": "...", "pemohon": "...", "keperluan": "...", "nama_barang": "...", "waktu_pinjam": "..."
            }
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
