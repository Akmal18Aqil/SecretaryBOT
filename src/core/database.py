import os
from supabase import create_client, Client
from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger("core.database")

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.client = None
        return cls._instance

    def connect(self):
        if self.client:
            return self.client
            
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_KEY
        
        if not url or not key:
            logger.warning("Supabase Creds missing! Database features will be disabled.")
            return None
            
        try:
            self.client: Client = create_client(url, key)
            logger.info("Connected to Supabase.")
            return self.client
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            return None

    def get_client(self):
        if not self.client:
            return self.connect()
        return self.client

    def check_access(self, telegram_id: int) -> bool:
        """
        Check if user is allowed to use the bot.
        """
        client = self.get_client()
        if not client:
            return True # Fail open if DB is down (or change to False for strict security)
            
        try:
            # Query table 'users'
            response = client.table('users').select("*").eq('telegram_id', telegram_id).eq('is_active', True).execute()
            
            # If data exists, user is allowed
            if response.data and len(response.data) > 0:
                logger.info(f"Access GRANTED for ID {telegram_id}")
                return True
            else:
                logger.warning(f"Access DENIED for ID {telegram_id}")
                return False
        except Exception as e:
            logger.error(f"Auth Check Error: {e}")
            return False # Fail safe

    def log_surat(self, data: dict):
        """
        Log created letter to 'surat_history'
        """
        client = self.get_client()
        if not client: return
        
        try:
            client.table('surat_history').insert(data).execute()
            logger.info("Surat logged to database.")
        except Exception as e:
            logger.error(f"Failed to log surat: {e}")

    def get_history(self, limit=5):
        """
        Fetch recent history for Recap
        """
        client = self.get_client()
        if not client: return []
        
        try:
            response = client.table('surat_history').select("*").order('created_at', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            return []

    def search_knowledge(self, query_embedding, match_threshold=0.5, match_count=3):
        """
        Search for similar documents using embeddings.
        """
        client = self.get_client()
        if not client: return []
        
        try:
            params = {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count
            }
            # RPC match_documents now returns (id, content, file_url, similarity)
            response = client.rpc("match_documents", params).execute()
            return response.data
        except Exception as e:
            logger.error(f"Search Knowledge Error: {e}")
            return []

db = Database()
