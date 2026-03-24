import sys
import argparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

import config
from handlers.commands import process_text
from services import lms_client, llm_router


# Обновленный tg_handler:
async def tg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    response = process_text(user_text)

    reply_markup = None
    # P1.3: Если пользователь пишет /start, показываем ему кнопки
    if user_text.strip().startswith("/start"):
        keyboard = [
            [
                InlineKeyboardButton(
                    "What labs are available?", callback_data="what labs are available"
                )
            ],
            [
                InlineKeyboardButton(
                    "Which lab has the lowest pass rate?",
                    callback_data="which lab has the lowest pass rate?",
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response, reply_markup=reply_markup)


# Обработчик нажатия на кнопки:
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Убираем "часики" загрузки на кнопке

    # Текст с кнопки отправляем в наш умный роутер
    response = process_text(query.data)
    await query.message.reply_text(response)


def run_telegram_bot():
    if not config.BOT_TOKEN:
        print("Error: BOT_TOKEN is missing in .env.bot.secret")
        sys.exit(1)

    app = Application.builder().token(config.BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tg_handler))
    app.add_handler(MessageHandler(filters.COMMAND, tg_handler))
    app.add_handler(CallbackQueryHandler(button_handler))  # Регистрируем кнопки

    print("Starting Telegram bot...")
    app.run_polling()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LMS Bot")
    parser.add_argument("--test", type=str, help="Run in test mode")
    args = parser.parse_args()

    if args.test:
        response = process_text(args.test)
        print(response)  # ВОТ ЭТА СТРОКА ОЧЕНЬ ВАЖНА!
        sys.exit(0)
    else:
        run_telegram_bot()
