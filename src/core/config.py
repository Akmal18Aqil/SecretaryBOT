import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env from root
load_dotenv()

class Settings:
    # Environment
    IS_VERCEL = bool(os.environ.get('VERCEL'))
    
    # Paths
    # src/core/config.py -> src/core -> src -> ROOT
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    TEMPLATE_DIR = BASE_DIR / "templates"
    
    # Output: /tmp in Vercel, ./output locally
    OUTPUT_DIR = Path("/tmp") if IS_VERCEL else BASE_DIR / "output"
    
    # Secrets
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    def ensure_dirs(self):
        if not self.IS_VERCEL and not self.OUTPUT_DIR.exists():
            self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            
settings = Settings()
