import os
import telebot
from src.workflow import graph_app
from src.core.logger import get_logger
from src.core.database import db
from src.utils.text import escape_markdown_v2

logger = get_logger("interface.telegram")

class TelegramInterface:
    def __init__(self, token):
        # threaded=False is CRITICAL for Vercel/Serverless
        self.bot = telebot.TeleBot(token, parse_mode=None, threaded=False)
        
        # Register Handlers
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message, "👋 Halo! Saya Secretary Swarm.\n\nSilakan perintahkan saya untuk membuat surat.\nContoh: 'Buatkan surat undangan rapat besok jam 8'")

        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            chat_id = message.chat.id
            user_input = message.text
            
            # --- AUTH CHECK ---
            if not db.check_access(chat_id):
                logger.warning(f"Unauthorized Access Attempt: {chat_id}")
                self.bot.reply_to(message, f"⛔ Maaf, ID Anda ({chat_id}) belum terdaftar sebagai pengurus.")
                return
            # ------------------
            
            # 1. Notify User Process Started
            msg_processing = self.bot.reply_to(message, "⏳ Sedang memproses...")
            
            try:
                # 2. Invoke LangGraph
                inputs = {
                    "user_input": user_input, 
                    # "telegram_id": chat_id # Pass ID to workflow if needed later
                    "telegram_id": chat_id
                }
                # Use Checkpointer Thread ID
                config = {"configurable": {"thread_id": str(chat_id)}}
                final_state = graph_app.invoke(inputs, config=config)
                
                # 3. Check Result
                if final_state.get('chat_reply'):
                    # Case A: Chat Mode / Recap
                    clean_reply = escape_markdown_v2(final_state['chat_reply'])
                    try:
                        self.bot.reply_to(message, clean_reply, parse_mode='MarkdownV2')
                    except Exception as e:
                        logger.warning(f"MarkdownV2 failed even after escaping: {e}")
                        # Fallback to plain text just in case
                        self.bot.reply_to(message, final_state['chat_reply'], parse_mode=None)
                    
                elif final_state.get('error'):
                    error_msg = final_state['error']
                    reply_text = f"🙏 Mohon Maaf\n\n{error_msg}\n\nSilakan lengkapi instruksi Anda agar saya bisa membantu. 📝"
                    self.bot.reply_to(message, reply_text) 
                
                elif final_state.get('approval_status') == 'PENDING':
                    # Document sent by Approver Node. Waiting for callback.
                    pass

                elif final_state.get('document_path'):
                    # Fallback for old flow or auto-approved
                    doc_path = final_state['document_path']
                    if os.path.exists(doc_path):
                        with open(doc_path, 'rb') as doc:
                            self.bot.send_document(chat_id, doc, caption="✅ Dokumen Siap!")
                    else:
                        self.bot.reply_to(message, "⚠️ Dokumen path ada, tapi file tidak ditemukan.")
                else:
                    self.bot.reply_to(message, "⚠️ Workflow selesai tanpa dokumen.")
                    
            except Exception as e:
                logger.error(f"Critical Bot Error: {e}", exc_info=True)
                self.bot.reply_to(message, f"💥 Critical Error: {str(e)}")
            
            # Optional: Delete 'processing' message to keep chat clean
            # self.bot.delete_message(chat_id, msg_processing.message_id)

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            if call.data == "ACC":
                self.bot.answer_callback_query(call.id, "Dokumen Disetujui ✅")
                self.bot.send_message(call.message.chat.id, "✅ **STATUS: FINAL**\nDokumen telah disetujui dan diarsipkan.", parse_mode="Markdown")
                # Here we could trigger a 'Finalizer' node if we wanted to move files
            elif call.data == "REVISI":
                self.bot.answer_callback_query(call.id, "Siap Revisi ❌")
                self.bot.send_message(call.message.chat.id, "❌ **STATUS: REVISI**\nSilakan ketik bagian mana yang perlu diperbaiki. Saya akan mendengarkan.")

    def start_polling(self):
        logger.info("🤖 Telegram Bot Berjalan...")
        # Remove Webhook first to prevent Conflict errors if previously on Vercel
        self.bot.remove_webhook()
        self.bot.infinity_polling()
