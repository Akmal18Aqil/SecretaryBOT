from typing import TypedDict, Optional

class AgentState(TypedDict):
    """
    State utama dari Secretary Swarm.
    Menyimpan semua konteks yang mengalir antar node.
    """
    user_input: str
    parsed_json: Optional[str]
    intent: Optional[str]      # e.g. 'undangan_internal'
    template_path: Optional[str]
    document_path: Optional[str]
    error: Optional[str]
