from services import lms_client
from services import llm_router

def handle_start() -> str:
    return "Welcome! I am the LMS Assistant bot. Type /help to see what I can do."

def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Lists all available commands\n"
        "/health - Reports healthy/unhealthy status of the backend\n"
        "/labs - Lists available labs\n"
        "/scores <lab> - Per-task scores for a specific lab (e.g., /scores lab-04)"
    )

def handle_health() -> str:
    return lms_client.get_health()

def handle_labs() -> str:
    return lms_client.get_labs()

def handle_scores(text: str) -> str:
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return "Missing lab argument. Usage: /scores <lab-id> (e.g., /scores lab-04)"
    
    lab_id = parts[1].strip()
    return lms_client.get_scores(lab_id)

def handle_unknown(text: str) -> str:
    return f"Unknown command. Type /help to see available commands."

def process_text(text: str) -> str:
    """Главный роутер для текстовых команд"""
    text = text.strip()
    
    if text.startswith("/start"):
        return handle_start()
    elif text.startswith("/help"):
        return handle_help()
    elif text.startswith("/health"):
        return handle_health()
    elif text.startswith("/labs"):
        return handle_labs()
    elif text.startswith("/scores"):
        return handle_scores(text)
    elif text.startswith("/"):
        return handle_unknown(text)
    else:
        return llm_router.route_intent(text)
