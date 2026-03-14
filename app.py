# app.py

from flask import Flask, request, jsonify
import os
import logging
import asyncio
from bot import main as bot_main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Создаём приложение бота
application = bot_main()

async def init_and_start():
    """Инициализация и запуск приложения."""
    await application.initialize()
    await application.start()
    logger.info("✅ Application инициализирован и запущен")

async def set_webhook():
    """Установка вебхука."""
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    logger.info(f"Устанавливаем вебхук на {webhook_url}")
    await application.bot.set_webhook(url=webhook_url)

# Выполняем асинхронную инициализацию при старте
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(init_and_start())
loop.run_until_complete(set_webhook())

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Эндпоинт для приёма обновлений от Telegram."""
    update_data = request.get_json()
    logger.info(f"Получено обновление: {update_data}")

    try:
        asyncio.run(application.process_update(update_data))
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления: {e}")

    return '', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
