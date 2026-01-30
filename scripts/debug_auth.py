import sys
import os

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import db

# ID from screenshot
TARGET_ID = 7944735177

print("--- DEBUG START ---")
try:
    print(f"Checking Access for ID: {TARGET_ID}")
    is_allowed = db.check_access(TARGET_ID)
    print(f"Result: {is_allowed}")
    
    # Check what IS in the database
    client = db.get_client()
    if client:
        print("Fetching ALL users...")
        res = client.table('users').select("*").execute()
        print(f"Data in DB: {res.data}")
    else:
        print("Client failed to initialize.")
        
except Exception as e:
    print(f"EXCEPTION: {e}")

print("--- DEBUG END ---")
