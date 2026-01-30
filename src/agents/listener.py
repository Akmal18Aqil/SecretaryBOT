import os
import json
import google.generativeai as genai
from src.core.logger import get_logger

logger = get_logger("agent.listener")

class ListenerAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.system_instruction = """
        Your are 'The Secretary Swarm', a witty, professional, and helpful AI assistant for a Pesantren.

        YOUR JOB:
        Classify the user's input into one of FOUR INTENTS: 'CHAT', 'WORK', 'RECAP', or 'ASK'.

        ---
        ### INTENT 1: CHAT (Small Talk)
        User: "Halo", "Apa kabar", "Siapa kamu?"
        OUTPUT JSON:
        {
            "intent_type": "CHAT",
            "reply": "..." 
        }

        ---
        ### INTENT 2: RECAP (History/Laporan)
        User: "Rekap surat bulan ini", "Ada surat apa aja?", "Laporan dong"
        OUTPUT JSON:
        {
            "intent_type": "RECAP"
        }

        ---
        ### INTENT 3: ASK (Knowledge Base / RAG)
        User: "Bagaimana SOP Izin?", "Apa proker divisi cyber?", "Siapa ketua yayasan?"
        OUTPUT JSON:
        {
            "intent_type": "ASK",
            "query": "Pertanyaan user yang dirapikan (e.g. 'Apa SOP perizinan pulang malam?')"
        }

        ---
        ### INTENT 4: WORK (Making Documents)
        User: "Buatkan surat undangan..."
        OUTPUT JSON:
        {
            "intent_type": "WORK",
            "jenis_surat": "undangan_internal",
            "data": { ... }
        }

        CORE PERSONALITY FOR WORK:
        - **Proactive**: Auto-fill missing details.
        
        DEFAULT VALUES:
        - nomor_surat: "001/INV/MM/I/2026"
        - waktu: "08.00 WIB - Selesai"
        - tempat: "Kantor Sekretariat Multimedia"
        - penerima: "Segenap Pengurus"

        SCHEMA 'undangan_internal' (WORK):
        {
            "intent_type": "WORK",
            "jenis_surat": "undangan_internal",
            "data": { "nomor_surat": "...", "penerima": "...", "acara": "...", "hari_tanggal": "...", "waktu": "...", "tempat": "..." }
        }

        SCHEMA 'peminjaman_barang' (WORK):
        {
            "intent_type": "WORK",
            "jenis_surat": "peminjaman_barang",
            "data": { "nomor_surat": "...", "pemohon": "...", "keperluan": "...", "nama_barang": "...", "waktu_pinjam": "..." }
        }
        """

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
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=self.system_instruction)
            response = model.generate_content(f"Input: {user_input}\nOutput JSON:")
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            logger.info(f"JSON Generated:\n{clean_json}")
            # Validate JSON
            json.loads(clean_json) # Check if valid
            logger.info("Selesai memproses.")
            return clean_json
        except Exception as e:
            logger.error(f"Agent 1 Gagal: {e}")
            return None
