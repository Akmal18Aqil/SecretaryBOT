import os
import json
from datetime import datetime
from docxtpl import DocxTemplate

class DrafterAgent:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_document(self, template_path, json_data):
        """
        Agent 3 Logic: Mengisi template Word.
        """
        try:
            data = json.loads(json_data)
            context = data.get('data')
            jenis_surat = data.get('jenis_surat')

            if not context:
                print("[Agent 3] ERROR: Data context kosong.")
                return None

            print(f"[Agent 3] Menulis dokumen...")
            doc = DocxTemplate(template_path)
            doc.render(context)

            # Generate Output Filename
            timestamp = datetime.now().strftime("%H%M%S")
            output_filename = f"SURAT_{jenis_surat}_{timestamp}.docx"
            output_path = os.path.join(self.output_dir, output_filename)
            
            doc.save(output_path)
            print(f"[Agent 3] Dokumen selesai: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[Agent 3] ERROR: {e}")
            return None
