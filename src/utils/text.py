import re

def escape_markdown_v2(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    Chars to escape: _ * [ ] ( ) ~ > # + - = | { } . !
    """
    if not text:
        return ""
        
    escape_chars = r'_*[]()~>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
