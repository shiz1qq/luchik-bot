from flask import Flask, jsonify
import threading
import asyncio
import os
import logging
import bot  # импортируем твоего бота

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def run_bot():
    """Запускает бота в отдельном потоке с собственным event loop."""
    logger.info("🟢 Запуск Telegram бота в отдельном потоке...")
    try:
        # Создаём новый event loop для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Запускаем функцию main() бота (она синхронная, но использует asyncio внутри)
        bot.main()
        
    except Exception as e:
        logger.error(f"🔴 Бот остановился с ошибкой: {e}")
    finally:
        loop.close()
        logger.info("🔴 Поток бота завершён.")

@app.route('/')
@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья Render."""
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("✅ Поток бота запущен, теперь запускаем Flask...")

    # Получаем порт из переменной окружения Render (по умолчанию 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
