# app.py

import os
import logging
import asyncio
import traceback
from flask import Flask, request, jsonify
from bot import main as bot_main

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Создаём и инициализируем приложение бота
application = bot_main()

async def init_bot():
    await application.initialize()
    await application.start()
    logger.info("Бот инициализирован и запущен")

async def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    logger.info(f"Устанавливаем вебхук на {webhook_url}")
    await application.bot.set_webhook(url=webhook_url)
    logger.info("Вебхук установлен")

# Выполняем инициализацию и установку вебхука при старте
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(init_bot())
loop.run_until_complete(set_webhook())

@app.errorhandler(Exception)
def handle_exception(e):
    """Глобальный обработчик исключений для Flask."""
    logger.error(f"Необработанное исключение: {e}\n{traceback.format_exc()}")
    return '', 500

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.info(f"Получен POST на /webhook: {data}")
    if not data:
        logger.warning("Пустой запрос")
        return '', 200

    try:
        asyncio.run(application.process_update(data))
    except Exception as e:
        logger.error(f"Ошибка при обработке обновления: {e}\n{traceback.format_exc()}")
    return '', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
