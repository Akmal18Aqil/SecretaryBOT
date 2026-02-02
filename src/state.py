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
    chat_reply: Optional[str]   # New: For small talk replies
    error: Optional[str]
    telegram_id: Optional[int]  # Required for sending callbacks
    approval_status: Optional[str] # PENDING, APPROVED, REJECTED
    audio_path: Optional[str]   # New: Path to temporary audio file (ogg)
