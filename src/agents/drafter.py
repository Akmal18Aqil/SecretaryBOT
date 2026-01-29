import os
import json
from datetime import datetime
from docxtpl import DocxTemplate
from src.core.logger import get_logger

logger = get_logger("agent.drafter")

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
            
            # Smart Context Detection:
            context = data.get('data', data) 
            jenis_surat = data.get('jenis_surat', 'dokumen')

            if not context:
                logger.error("Data context kosong.")
                return None

            logger.info("Menulis dokumen...")
            doc = DocxTemplate(template_path)
            doc.render(context)

            # Generate Output Filename
            timestamp = datetime.now().strftime("%H%M%S")
            output_filename = f"SURAT_{jenis_surat}_{timestamp}.docx"
            output_path = os.path.join(self.output_dir, output_filename)
            
            doc.save(output_path)
            logger.info(f"Dokumen selesai: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Generate Document Error: {e}")
            return None
