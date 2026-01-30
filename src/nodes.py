import json
from src.state import AgentState
from src.agents.listener import ListenerAgent
from src.agents.clerk import ClerkAgent
from src.agents.drafter import DrafterAgent
from src.agents.archivist import ArchivistAgent
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

def node_listener(state: AgentState):
    """
    Node 1: Listener
    """
    logger.info("Node: Listener Active")
    user_input = state['user_input']
    
    # 0. Check Auth (Simple Logic) - Can be moved to Telegram Interface strictly
    # But good to have here if we expand interfaces
    
    json_result = listener_agent.process_request(user_input)
    
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
                
            # Case C: Work Mode
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

def node_notifier(state: AgentState):
    """
    Node 4: Notifier (Disabled)
    """
    logger.info("Node: Notifier (Skipped)")
    return {}
