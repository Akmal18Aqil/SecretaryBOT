import os

class ClerkAgent:
    def __init__(self, template_dir='templates'):
        self.template_dir = template_dir
        
    def get_template_path(self, jenis_surat):
        """
        Agent 2 Logic: Memilih file template.
        """
        # Mapping nama template
        # Di sistem produksi, ini bisa dari database atau scan file
        tpl_filename = f"tpl_{jenis_surat}.docx"
        tpl_path = os.path.join(self.template_dir, tpl_filename)

        if not os.path.exists(tpl_path):
            print(f"[Agent 2] WARNING: Template tidak ditemukan: {tpl_path}")
            print(f"[Agent 2] Menggunakan fallback template 'tpl_undangan_internal.docx' jika ada.")
            fallback = os.path.join(self.template_dir, 'tpl_undangan_internal.docx')
            if os.path.exists(fallback):
                return fallback
            else:
                return None
        
        print(f"[Agent 2] Template ditemukan: {tpl_filename}")
        return tpl_path
