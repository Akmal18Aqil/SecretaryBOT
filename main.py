import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings
from src.interfaces.telegram_bot import TelegramInterface

def main():
    print("=== THE SECRETARY SWARM (ONLINE MODE) ===")
    
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        print("[ERROR] TELEGRAM_BOT_TOKEN belum diisi di .env!")
        print("Silakan buat bot di @BotFather dan masukkan tokennya.")
        return

    # Init & Start Bot
    bot_interface = TelegramInterface(token)
    bot_interface.start_polling()

if __name__ == "__main__":
    main()
