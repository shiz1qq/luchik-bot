# bot.py

import os
import logging
import time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import Session, init_db, get_user, save_dream, get_last_dreams, save_mood
from openai_client import ask_gpt, interpret_dream
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()

def main_keyboard():
    """Клавиатура с основными кнопками."""
    keyboard = [
        [KeyboardButton("☀️ Доброе утро")],
        [KeyboardButton("🌙 Рассказать сон")],
        [KeyboardButton("📖 Мои сны")],
        [KeyboardButton("💬 Просто поболтать")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    with Session() as session:
        get_user(session, user.id, user.first_name, user.username)
    # Сохраняем имя Зиниры в user_data
    context.user_data['user_name'] = "Зинира"
    await update.message.reply_text(
        f"Привет, Зинира! 🌸\nЯ Лучик — твой друг и помощник.\nВыбирай:",
        reply_markup=main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    await update.message.reply_text(
        "Я умею:\n"
        "☀️ Доброе утро – тёплое приветствие\n"
        "🌙 Толковать сны – расскажи сон, и я помогу понять его\n"
        "📖 Мои сны – показать последние сны\n"
        "💬 Просто поболтать – поговорим о чём хочешь"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Основной обработчик текстовых сообщений."""
    text = update.message.text
    user = update.effective_user
    user_name = context.user_data.get('user_name', user.first_name or 'милая')

    logger.info(f"📝 Получено сообщение от {user_name}: {text[:50]}...")

    # Обработка кнопок
    if text == "☀️ Доброе утро":
        response = ask_gpt(
            f"Напиши тёплое утреннее приветствие для {user_name}, "
            "пожелай хорошего дня, скажи комплимент. Используй смайлики."
        )
        await update.message.reply_text(response)

    elif text == "🌙 Рассказать сон":
        await update.message.reply_text(
            "Расскажи мне свой сон в деталях. Я постараюсь его понять и истолковать ✨"
        )
        context.user_data['expecting_dream'] = True

    elif text == "📖 Мои сны":
        with Session() as session:
            dreams = get_last_dreams(session, user.id, limit=5)
        if not dreams:
            await update.message.reply_text("Ты пока не записывала свои сны. Расскажешь мне первый? 🌙")
        else:
            msg = "Вот твои последние сны:\n"
            for d in dreams:
                date = d.created_at.strftime("%d.%m")
                preview = d.dream_text[:50] + "..." if len(d.dream_text) > 50 else d.dream_text
                msg += f"\n📅 {date}: {preview}"
            await update.message.reply_text(msg)

    elif text == "💬 Просто поболтать":
        await update.message.reply_text("О чём хочешь поговорить? Я слушаю 💬")
        context.user_data['expecting_chat'] = True

    else:
        # Обычное сообщение (не кнопка)
        if context.user_data.get('expecting_dream'):
            # Ждём описание сна
            dream_text = text
            await update.message.reply_text("Дай-ка подумаю над твоим сном... 🔮")
            interpretation = interpret_dream(dream_text)
            with Session() as session:
                save_dream(session, user.id, dream_text, interpretation)
            await update.message.reply_text(interpretation)
            await update.message.reply_text("А какое у тебя сейчас настроение после этого сна?")
            context.user_data['expecting_dream'] = False
            context.user_data['expecting_mood'] = True

        elif context.user_data.get('expecting_mood'):
            # Ждём настроение
            mood = text
            with Session() as session:
                save_mood(session, user.id, mood)
            await update.message.reply_text("Спасибо, что поделилась, Зинира. Береги себя 💖")
            context.user_data['expecting_mood'] = False

        elif context.user_data.get('expecting_chat'):
            # Свободный разговор
            response = ask_gpt(
                f"{user_name} пишет: {text}\n"
                "Ответь ей как заботливый друг Лучик, коротко и тепло."
            )
            await update.message.reply_text(response)
            context.user_data['expecting_chat'] = False

        else:
            # Обычный диалог (без ожидания)
            response = ask_gpt(
                f"{user_name} пишет: {text}\n"
                "Ответь ей как заботливый друг Лучик."
            )
            await update.message.reply_text(response)

    logger.info(f"✅ Обработка сообщения от {user_name} завершена")

def main():
    """Создаёт и возвращает Application с настроенными обработчиками."""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("❌ TELEGRAM_TOKEN не задан в переменных окружения")

    # Создаём Application, отключая встроенный Updater (мы используем вебхуки)
    application = Application.builder().token(token).updater(None).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application
