# app.py

import os
import logging
import asyncio
import threading
import traceback
from flask import Flask, request, jsonify
from bot import main as bot_main

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Создаём приложение бота
application = bot_main()

# Глобальные переменные для фонового цикла событий
background_loop = None
background_thread = None

async def init_bot():
    """Инициализация и запуск бота."""
    await application.initialize()
    await application.start()
    logger.info("✅ Бот инициализирован и запущен")

async def set_webhook():
    """Установка вебхука."""
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    logger.info(f"📡 Устанавливаем вебхук на {webhook_url}")
    await application.bot.set_webhook(url=webhook_url)
    logger.info("✅ Вебхук установлен")

def start_background_loop(loop):
    """Запускает цикл событий в фоновом потоке."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Создаём и запускаем фоновый цикл событий
background_loop = asyncio.new_event_loop()
background_thread = threading.Thread(target=start_background_loop, args=(background_loop,), daemon=True)
background_thread.start()

# Выполняем инициализацию и установку вебхука в фоновом цикле
init_future = asyncio.run_coroutine_threadsafe(init_bot(), background_loop)
init_future.result(timeout=10)  # ждём до 10 секунд

webhook_future = asyncio.run_coroutine_threadsafe(set_webhook(), background_loop)
webhook_future.result(timeout=10)

@app.errorhandler(Exception)
def handle_exception(e):
    """Глобальный обработчик исключений."""
    logger.error(f"❌ Необработанное исключение: {e}\n{traceback.format_exc()}")
    return '', 500

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука от Telegram."""
    data = request.get_json()
    logger.info(f"📩 Получен POST на /webhook: {data}")

    if not data:
        logger.warning("⚠️ Пустой запрос")
        return '', 200

    # Отправляем задачу в фоновый цикл событий
    future = asyncio.run_coroutine_threadsafe(application.process_update(data), background_loop)

    try:
        # Ждём завершения обработки с таймаутом, чтобы не блокировать Flask
        future.result(timeout=5)
    except asyncio.TimeoutError:
        logger.warning("⏱️ Обработка обновления заняла больше 5 секунд")
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке обновления: {e}\n{traceback.format_exc()}")

    return '', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
