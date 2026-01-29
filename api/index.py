import os
import sys
from flask import Flask, request
import telebot

# Add root project to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import settings
from src.interfaces.telegram_bot import TelegramInterface

app = Flask(__name__)
token = settings.TELEGRAM_BOT_TOKEN

# Global Bot Instance
bot_interface = None
if token:
    bot_interface = TelegramInterface(token)

@app.route('/', methods=['GET'])
def index():
    return "The Secretary Swarm is awake and listening! 🤖"

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Terima update dari Telegram via Webhook
    """
    if not bot_interface:
        return "Bot Token not configured", 500
    
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        # Process update (Synchronous)
        bot_interface.bot.process_new_updates([update])
        
        return "OK", 200
    else:
        return "Content-Type must be application/json", 403

# Local testing only
if __name__ == "__main__":
    app.run(debug=True, port=3000)
