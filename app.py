# app.py
from flask import Flask, jsonify
import threading
import os
import sys
import logging

# Импортируем твоего основного бота. Предполагается, что твой файл называется bot.py
# и в нём есть функция main(), которая запускает application.run_polling()
import bot

# Настраиваем логгирование, чтобы видеть, что происходит
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Функция для запуска твоего бота в отдельном потоке
def run_bot():
    logger.info("Запуск Telegram бота в отдельном потоке...")
    try:
        # Здесь вызывается твоя функция main() из файла bot.py
        bot.main()
    except Exception as e:
        logger.error(f"Бот остановился с ошибкой: {e}")

# Эндпоинт для проверки здоровья (health check) Render'ом
@app.route('/')
@app.route('/health')
def health():
    """Эндпоинт, который Render будет проверять, чтобы сервис не "засыпал"."""
    return jsonify({"status": "ok", "message": "Bot is running"}), 200

# Запускаем всё при старте приложения
if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Поток завершится, когда завершится main
    bot_thread.start()
    logger.info("Поток бота запущен, теперь запускаем Flask...")

    # Запускаем Flask-сервер, слушая порт, который даст Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
