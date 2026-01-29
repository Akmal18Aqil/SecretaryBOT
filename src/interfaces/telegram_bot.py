import os
import telebot
from src.workflow import graph_app

class TelegramInterface:
    def __init__(self, token):
        # threaded=False is CRITICAL for Vercel/Serverless
        # Otherwise the process exits before the reply is sent
        self.bot = telebot.TeleBot(token, parse_mode=None, threaded=False)
        
        # Register Handlers
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message, "👋 Halo! Saya Secretary Swarm.\n\nSilakan perintahkan saya untuk membuat surat.\nContoh: 'Buatkan surat undangan rapat besok jam 8'")

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            chat_id = message.chat.id
            user_input = message.text
            
            # 1. Notify User Process Started
            msg_processing = self.bot.reply_to(message, "⏳ Sedang memproses...")
            
            try:
                # 2. Invoke LangGraph
                inputs = {"user_input": user_input}
                final_state = graph_app.invoke(inputs)
                
                # 3. Check Result
                # 3. Check Result
                if final_state.get('error'):
                    error_msg = final_state['error']
                    reply_text = f"🙏 Mohon Maaf\n\n{error_msg}\n\nSilakan lengkapi instruksi Anda agar saya bisa membantu. 📝"
                    self.bot.reply_to(message, reply_text) # Removed parse_mode='Markdown' to prevent crashes
                elif final_state.get('document_path'):
                    doc_path = final_state['document_path']
                    if os.path.exists(doc_path):
                        with open(doc_path, 'rb') as doc:
                            self.bot.send_document(chat_id, doc, caption="✅ Dokumen Siap!")
                    else:
                        self.bot.reply_to(message, "⚠️ Dokumen path ada, tapi file tidak ditemukan.")
                else:
                    self.bot.reply_to(message, "⚠️ Workflow selesai tanpa dokumen.")
                    
            except Exception as e:
                self.bot.reply_to(message, f"💥 Critical Error: {str(e)}")
            
            # Optional: Delete 'processing' message to keep chat clean
            # self.bot.delete_message(chat_id, msg_processing.message_id)

    def start_polling(self):
        print("🤖 Telegram Bot Berjalan...")
        self.bot.infinity_polling()
