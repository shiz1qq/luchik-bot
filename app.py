# app.py (финальная версия)

from flask import Flask, request, jsonify
import os
import logging
import asyncio
from bot import main as bot_main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
application = bot_main()

async def init_and_start():
    await application.initialize()
    await application.start()
    logger.info("✅ Application инициализирован и запущен")

async def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    logger.info(f"Устанавливаем вебхук на {webhook_url}")
    await application.bot.set_webhook(url=webhook_url)

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
    update_data = request.get_json()
    try:
        asyncio.run(application.process_update(update_data))
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления: {e}")
    return '', 200
