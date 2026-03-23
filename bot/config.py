import os
from dotenv import load_dotenv

load_dotenv(".env.bot.secret")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LMS_API_BASE_URL = os.getenv("LMS_API_BASE_URL", "http://localhost:42002")
LMS_API_KEY = os.getenv("LMS_API_KEY", "")

# Новые переменные для LLM
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE_URL = os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1")
LLM_API_MODEL = os.getenv("LLM_API_MODEL", "qwen2.5-coder-7b-instruct")
