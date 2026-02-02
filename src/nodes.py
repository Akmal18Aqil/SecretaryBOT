import json
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.state import AgentState
from src.agents.listener import ListenerAgent
from src.agents.clerk import ClerkAgent
from src.agents.drafter import DrafterAgent
from src.agents.archivist import ArchivistAgent
from src.agents.librarian import LibrarianAgent
from src.core.config import settings
from src.core.logger import get_logger
from src.core.database import db

logger = get_logger("workflow.node")

# Ensure Output Dir Exists
settings.ensure_dirs()

# Init Agents
listener_agent = ListenerAgent(api_key=settings.GOOGLE_API_KEY)
clerk_agent = ClerkAgent(template_dir=str(settings.TEMPLATE_DIR)) 
drafter_agent = DrafterAgent(output_dir=str(settings.OUTPUT_DIR))
archivist_agent = ArchivistAgent()
librarian_agent = LibrarianAgent(api_key=settings.GOOGLE_API_KEY)

def node_listener(state: AgentState):
    """
    Node 1: Listener
    """
    logger.info("Node: Listener Active")
    user_input = state['user_input']
    
    # 0. Check Auth (Simple Logic) - Can be moved to Telegram Interface strictly
    # But good to have here if we expand interfaces
    
    # Extract History from State
    history = state.get('parsed_json')
    audio_path = state.get('audio_path')
    json_result = listener_agent.process_request(user_input, history_context=history, audio_path=audio_path)
    
    updates = {'parsed_json': json_result}
    
    try:
        if json_result:
            parsed = json.loads(json_result)
            
            # Check for Friendly Error
            if 'error' in parsed:
                updates['error'] = parsed['error']
            
            # Case A: Chat Mode
            elif parsed.get('intent_type') == 'CHAT':
                updates['chat_reply'] = parsed.get('reply')

            # Case B: Recap Mode
            elif parsed.get('intent_type') == 'RECAP':
                recap_text = archivist_agent.get_recap()
                updates['chat_reply'] = recap_text
            
            # Case C: Ask Mode (RAG)
            elif parsed.get('intent_type') == 'ASK':
                query = parsed.get('query')
                answer = librarian_agent.answer_question(query)
                updates['chat_reply'] = answer
                
            # Case D: Work Mode
            else:
                updates['intent'] = parsed.get('jenis_surat')
        else:
            updates['error'] = "Listener failed to generate JSON"
    except Exception as e:
        logger.error(f"JSON Parse Error: {e}")
        updates['error'] = f"JSON Parse Error: {str(e)}"
        
    return updates

def node_clerk(state: AgentState):
    """
    Node 2: Clerk
    """
    # SKIP if Error OR Chat Mode OR Recap Mode
    if state.get('error') or state.get('chat_reply'):
        return {} 

    logger.info("Node: Clerk Active")
    intent = state.get('intent')
    
    if not intent:
        return {'error': "Clerk: No intent detected."}
        
    template_path = clerk_agent.get_template_path(intent)
    
    if not template_path:
        error_msg = f"Clerk: Template not found for '{intent}' in {settings.TEMPLATE_DIR}"
        logger.error(error_msg)
        return {'error': error_msg}
        
    return {'template_path': template_path}

def node_drafter(state: AgentState):
    """
    Node 3: Drafter
    """
    # SKIP if Error OR Chat Mode
    if state.get('error') or state.get('chat_reply'):
        return {} 

    logger.info("Node: Drafter Active")
    json_data = state.get('parsed_json')
    template_path = state.get('template_path')
    
    if not json_data or not template_path:
        error_msg = f"Drafter: Missing data. JSON: {bool(json_data)}, TPL: {bool(template_path)}"
        logger.error(error_msg)
        return {'error': error_msg}
        
    doc_path = drafter_agent.generate_document(template_path, json_data)
    
    if not doc_path:
        return {'error': "Drafter failed to save document"}

    # LOG TO DATABASE
    try:
        parsed = json.loads(json_data)
        db.log_surat({
            "nomor_surat": parsed.get('data', {}).get('nomor_surat'),
            "jenis_surat": parsed.get('jenis_surat'),
            "detail_json": parsed,
            # "dibuat_oleh": telegram_id # Idealnya dipassing dari state
        })
    except Exception as e:
        logger.warning(f"Failed to log to DB: {e}")
        
    return {'document_path': doc_path}

def node_approver(state: AgentState):
    """
    Node 3.5: Approver (Human in the Loop)
    Sends the draft to the user for confirmation.
    """
    # SKIP if Error OR Chat Mode
    if state.get('error') or state.get('chat_reply'):
        return {}

    logger.info("Node: Approver Active")
    doc_path = state.get('document_path')
    telegram_id = state.get('telegram_id')

    if not doc_path or not telegram_id:
        logger.warning(f"Approver skipped: Missing doc_path ({doc_path}) or telegram_id ({telegram_id})")
        return {}

    # Initialize Bot for Sending Message (Stateless usage)
    bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

    # Prepare Buttons
    markup = InlineKeyboardMarkup()
    btn_acc = InlineKeyboardButton("✅ Setujui (Final)", callback_data="ACC")
    btn_reject = InlineKeyboardButton("❌ Revisi", callback_data="REVISI")
    markup.add(btn_acc, btn_reject)

    # Send Document
    try:
        if os.path.exists(doc_path):
            with open(doc_path, 'rb') as doc:
                bot.send_document(
                    chat_id=telegram_id, 
                    document=doc, 
                    caption="📄 **DRAFT SURAT**\n\nMohon diperiksa sebelum difinalisasi.",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            logger.info(f"Draft sent to {telegram_id} for approval.")
            return {'approval_status': 'PENDING'}
        else:
            logger.error(f"Document not found at {doc_path}")
            return {'error': "Document lost before approval."}
    except Exception as e:
        logger.error(f"Failed to send draft: {e}")
        return {'error': f"Failed to send draft: {str(e)}"}


def node_notifier(state: AgentState):
    """
    Node 4: Notifier (Pass-through)
    """
    logger.info("Node: Workflow Complete. Handoff to Interface.")
    return {}
