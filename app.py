# app.py

from flask import Flask, request, jsonify
import os
import logging
import asyncio
from bot import main as bot_main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Создаём приложение бота один раз при старте
application = bot_main()

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

@app.route(f'/webhook', methods=['POST'])
def webhook():
    """Эндпоинт для приёма обновлений от Telegram"""
    update = request.get_json()
    logger.info(f"Получено обновление: {update}")
    
    # Обрабатываем обновление асинхронно
    asyncio.create_task(application.process_update(update))
    
    return '', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    # Устанавливаем вебхук при запуске
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    logger.info(f"Устанавливаем вебхук на {webhook_url}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.bot.set_webhook(url=webhook_url))
    
    # Запускаем Flask
    app.run(host='0.0.0.0', port=port)
