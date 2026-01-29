import os
import json
import google.generativeai as genai

class ListenerAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.system_instruction = """
        You are 'The Secretary Swarm', an intelligent administrative assistant.
        Your goal is to extract structured data for document generation.

        RULES:
        1. Output strictly valid JSON.
        2. Identify 'jenis_surat' (undangan_internal / peminjaman_barang).
        3. Convert dates to Indonesian Format (e.g., "Senin, 30 Januari 2026").
        4. USE EXACT KEYS BELOW (Do not make up new keys):

        SCHEMA 'undangan_internal':
        {
            "jenis_surat": "undangan_internal",
            "data": {
                "nomor_surat": "001/INV/MM/I/2026",
                "penerima": "...", 
                "acara": "...",
                "hari_tanggal": "...",
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

        If info is missing, return {"error": "..."}.
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
