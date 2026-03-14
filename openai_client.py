# openai_client.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Настраиваем Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ Нет GEMINI_API_KEY в .env файле")

genai.configure(api_key=API_KEY)

# Системный промпт с именем Зинира
SYSTEM_PROMPT = """
Ты — заботливый друг по имени Лучик. Твоя задача: поддерживать девушку по имени Зинира,
говорить ей комплименты, интересоваться ее делами и помогать интерпретировать сны.
Ты говоришь мягко, используешь нежные смайлики, никогда не осуждаешь.
Обращайся к ней по имени Зинира.
Если просят истолковать сон, ты даешь психологическую или метафорическую интерпретацию,
но всегда подчеркиваешь, что это лишь идеи, а истинный смысл знает только она.
Используй вопросы, чтобы лучше понять контекст сна.
"""

# Выбираем модель. Gemini 3.1 Flash Lite — быстрая и экономичная [citation:10]
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT
)

def ask_gpt(user_message: str) -> str:
    try:
        response = model.generate_content(
            user_message,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                max_output_tokens=500
            )
        )
        return response.text
    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        import traceback
        traceback.print_exc()
        return "Извини, я немного завис. Попробуй еще раз через минутку 💫"

def interpret_dream(dream_text: str) -> str:
    prompt = f"Зинира рассказала мне сон. Помоги разобраться, что он может означать: {dream_text}"
    return ask_gpt(prompt)
