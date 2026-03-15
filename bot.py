# bot.py

import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Session, init_db, get_user, save_dream, get_last_dreams, save_mood
from openai_client import ask_gpt, interpret_dream
from dotenv import load_dotenv

load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

init_db()

def main_keyboard():
    keyboard = [
        [KeyboardButton("☀️ Доброе утро")],
        [KeyboardButton("🌙 Рассказать сон")],
        [KeyboardButton("📖 Мои сны")],
        [KeyboardButton("💬 Просто поболтать")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with Session() as session:
        get_user(session, user.id, user.first_name, user.username)
    context.user_data['user_name'] = "Зинира"
    await update.message.reply_text(
        f"Привет, Зинира! 🌸\nЯ Лучик — твой друг и помощник.\nВыбирай:",
        reply_markup=main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я умею: ☀️ Доброе утро, 🌙 Толковать сны, 📖 История, 💬 Поболтать")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    user_name = context.user_data.get('user_name', user.first_name or 'милая')

    if text == "☀️ Доброе утро":
        response = ask_gpt(f"Напиши тёплое утреннее приветствие для {user_name}, пожелай хорошего дня, скажи комплимент.")
        await update.message.reply_text(response)

    elif text == "🌙 Рассказать сон":
        await update.message.reply_text("Расскажи свой сон...")
        context.user_data['expecting_dream'] = True

    elif text == "📖 Мои сны":
        with Session() as session:
            dreams = get_last_dreams(session, user.id, limit=5)
        if not dreams:
            await update.message.reply_text("Снов пока нет.")
        else:
            msg = "Последние сны:\n"
            for d in dreams:
                date = d.created_at.strftime("%d.%m")
                preview = d.dream_text[:50] + "..." if len(d.dream_text) > 50 else d.dream_text
                msg += f"\n📅 {date}: {preview}"
            await update.message.reply_text(msg)

    elif text == "💬 Просто поболтать":
        await update.message.reply_text("О чём поговорим?")
        context.user_data['expecting_chat'] = True

    else:
        if context.user_data.get('expecting_dream'):
            dream_text = text
            await update.message.reply_text("Думаю...")
            interpretation = interpret_dream(dream_text)
            with Session() as session:
                save_dream(session, user.id, dream_text, interpretation)
            await update.message.reply_text(interpretation)
            await update.message.reply_text("Какое настроение после сна?")
            context.user_data['expecting_dream'] = False
            context.user_data['expecting_mood'] = True
        elif context.user_data.get('expecting_mood'):
            mood = text
            with Session() as session:
                save_mood(session, user.id, mood)
            await update.message.reply_text("Спасибо, Зинира! Береги себя.")
            context.user_data['expecting_mood'] = False
        elif context.user_data.get('expecting_chat'):
            response = ask_gpt(f"{user_name} пишет: {text}\nОтветь ей как друг.")
            await update.message.reply_text(response)
            context.user_data['expecting_chat'] = False
        else:
            response = ask_gpt(f"{user_name} пишет: {text}\nОтветь ей как друг.")
            await update.message.reply_text(response)

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN не задан")
    # Отключаем встроенный Updater, так как мы используем вебхуки
    application = Application.builder().token(token).updater(None).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return application
