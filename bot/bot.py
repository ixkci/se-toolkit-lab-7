import sys
import argparse
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import config
from handlers.commands import process_text


# --- Telegram обертки ---
async def tg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    response = process_text(user_text)
    await update.message.reply_text(response)


def run_telegram_bot():
    if not config.BOT_TOKEN:
        print("Error: BOT_TOKEN is missing in .env.bot.secret")
        sys.exit(1)

    app = Application.builder().token(config.BOT_TOKEN).build()

    # Перенаправляем все текстовые сообщения и команды в наш универсальный обработчик
    app.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, tg_handler))

    print("Starting Telegram bot...")
    app.run_polling()


# --- Точка входа ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LMS Bot")
    parser.add_argument(
        "--test",
        type=str,
        help="Run in test mode with a specific command (e.g. '/start')",
    )
    args = parser.parse_args()

    if args.test:
        # Режим тестирования в терминале (без Telegram)
        response = process_text(args.test)
        print(response)
        sys.exit(0)
    else:
        # Обычный режим (Telegram)
        run_telegram_bot()
