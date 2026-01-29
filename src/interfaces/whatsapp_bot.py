import pywhatkit as kit
import time
import os

class WhatsAppInterface:
    def __init__(self, target_number=None):
        self.target_number = target_number
        
    def send_notification(self, message):
        """
        Mengirim pesan teks ke WhatsApp.
        """
        if not self.target_number:
            print("[WA Bot] Target number belum diset. Lewati pengiriman WA.")
            return

        print(f"[WA Bot] Bersiap mengirim pesan ke {self.target_number}...")
        try:
            # wait_time set to 15 seconds to allow browser to open
            # tab_close set to True to close after sending
            kit.sendwhatmsg_instantly(self.target_number, message, wait_time=15, tab_close=True)
            print("[WA Bot] Pesan terkirim!")
        except Exception as e:
            print(f"[WA Bot] Gagal mengirim pesan: {e}")

    def send_document_alert(self, document_path):
        """
        Memberi tahu user bahwa dokumen sudah jadi.
        NOTE: PyWhatKit versi standar belum stabil untuk kirim file dokumen (.docx) 
        tanpa interaksi GUI yang kompleks. Jadi kita kirim notifikasi saja.
        """
        filename = os.path.basename(document_path)
        msg = f"✅ *The Secretary Swarm* Melapor!\n\nDokumen Anda telah selesai:\n📂 *{filename}*\n\nSilakan cek folder Output di laptop Anda."
        self.send_notification(msg)
