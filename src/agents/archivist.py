from src.core.database import db
from src.core.logger import get_logger

logger = get_logger("agent.archivist")

class ArchivistAgent:
    def __init__(self):
        self.db = db

    def get_recap(self, limit=5):
        """
        Agent 4 Logic: Membuat laporan rekap surat terakhir.
        """
        logger.info("Mengambil data rekap dari database...")
        history = self.db.get_history(limit=limit)
        
        if not history:
            return "📭 Belum ada riwayat surat yang tercatat."
            
        # Format Laporan
        report = ["📊 **REKAP SURAT TERAKHIR**\n"]
        
        for idx, item in enumerate(history, 1):
            # Parse timestamp if needed, or just use raw for now
            created_at = item.get('created_at', '')[:10] # Ambil YYYY-MM-DD
            jenis = item.get('jenis_surat', 'Dokumen')
            nomor = item.get('nomor_surat', '-')
            
            report.append(f"{idx}. **{jenis}**")
            report.append(f"   📅 {created_at} | 🏷️ {nomor}")
            report.append("")
            
        report.append("💡 _Data diambil dari Supabase Cloud_")
        return "\n".join(report)
