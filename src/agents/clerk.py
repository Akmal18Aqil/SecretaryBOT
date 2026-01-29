import os
from src.core.logger import get_logger

logger = get_logger("agent.clerk")

class ClerkAgent:
    def __init__(self, template_dir='templates'):
        self.template_dir = template_dir
        
    def get_template_path(self, jenis_surat):
        """
        Agent 2 Logic: Memilih file template.
        """
        tpl_filename = f"tpl_{jenis_surat}.docx"
        tpl_path = os.path.join(self.template_dir, tpl_filename)

        if not os.path.exists(tpl_path):
            logger.warning(f"Template tidak ditemukan: {tpl_path}")
            logger.info("Mencoba fallback ke 'tpl_undangan_internal.docx'")
            
            fallback = os.path.join(self.template_dir, 'tpl_undangan_internal.docx')
            if os.path.exists(fallback):
                return fallback
            else:
                return None
        
        logger.info(f"Template ditemukan: {tpl_filename}")
        return tpl_path
