def handle_start() -> str:
    return "Hello! I am your LMS bot. Type /help to see available commands."


def handle_help() -> str:
    return "Available commands: /start, /help, /health, /labs, /scores"


def handle_health() -> str:
    return "Backend status: OK (Placeholder)"


def handle_unknown(text: str) -> str:
    return f"Received: {text} (Not implemented yet)"


def process_text(text: str) -> str:
    """Главный роутер для текстовых команд"""
    text = text.strip()
    if text.startswith("/start"):
        return handle_start()
    elif text.startswith("/help"):
        return handle_help()
    elif text.startswith("/health"):
        return handle_health()
    else:
        return handle_unknown(text)
