# openai_client.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY не задан")

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
Ты — заботливый друг по имени Лучик. Твоя задача: поддерживать девушку по имени Зинира,
говорить ей комплименты, интересоваться ее делами и помогать интерпретировать сны.
Ты говоришь мягко, используешь нежные смайлики.
Обращайся к ней по имени.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT
)

def ask_gpt(user_message: str) -> str:
    try:
        response = model.generate_content(user_message, generation_config=genai.types.GenerationConfig(temperature=0.8, max_output_tokens=500))
        return response.text
    except Exception as e:
        return f"Извини, ошибка: {e}"

def interpret_dream(dream_text: str) -> str:
    return ask_gpt(f"Что означает этот сон? {dream_text}")
