import os
import json
from dotenv import load_dotenv

from src.state import AgentState
from src.agents.listener import ListenerAgent
from src.agents.clerk import ClerkAgent
from src.agents.drafter import DrafterAgent
# from src.interfaces.whatsapp_bot import WhatsAppInterface

# Init Agents (Global instantiation for reuse)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
# MY_PHONE = os.getenv("MY_PHONE_NUMBER")

listener_agent = ListenerAgent(api_key=API_KEY)
clerk_agent = ClerkAgent(template_dir='templates')
drafter_agent = DrafterAgent(output_dir='output')
# wa_bot = WhatsAppInterface(target_number=MY_PHONE)

def node_listener(state: AgentState):
    """
    Node 1: Listener
    Menerima input user -> Output JSON & Intent
    """
    print(f"\n[GRAPH] Node: Listener Active")
    user_input = state['user_input']
    
    json_result = listener_agent.process_request(user_input)
    
    updates = {'parsed_json': json_result}
    
    # Try parsing 'jenis_surat' for Router intent
    try:
        if json_result:
            parsed = json.loads(json_result)
            
            # Check if AI returned an error (friendly error)
            if 'error' in parsed:
                updates['error'] = parsed['error']
            else:
                updates['intent'] = parsed.get('jenis_surat')
        else:
            updates['error'] = "Listener failed to generate JSON"
    except Exception as e:
        updates['error'] = f"JSON Parse Error: {str(e)}"
        
    return updates

def node_clerk(state: AgentState):
    """
    Node 2: Clerk
    Menerima Intent -> Output Template Path
    """
    print(f"[GRAPH] Node: Clerk Active")
    intent = state.get('intent')
    
    if not intent:
        return {'error': "No intent found for Clerk"}
        
    template_path = clerk_agent.get_template_path(intent)
    
    if not template_path:
        return {'error': f"Template not found for type: {intent}"}
        
    return {'template_path': template_path}

def node_drafter(state: AgentState):
    """
    Node 3: Drafter
    Menerima JSON + Template -> Output Document Path
    """
    print(f"[GRAPH] Node: Drafter Active")
    json_data = state.get('parsed_json')
    template_path = state.get('template_path')
    
    if not json_data or not template_path:
        return {'error': "Missing data for Drafter"}
        
    doc_path = drafter_agent.generate_document(template_path, json_data)
    
    if not doc_path:
        return {'error': "Drafter failed to save document"}
        
    return {'document_path': doc_path}

def node_notifier(state: AgentState):
    """
    Node 4: Notifier (Disabled)
    """
    print(f"[GRAPH] Node: Notifier (Skipped per user request)")
    # doc_path = state.get('document_path')
    # if doc_path:
    #     wa_bot.send_document_alert(doc_path)
    
    return {} # No state update needed
