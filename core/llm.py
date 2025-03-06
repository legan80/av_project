from core.settings import openai_key, model_api_url
from core.logging_config import setup_logger
from lexicon.prompts import prompt_openai_simple_ru

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

# Настройка логирования
logger = setup_logger()

# Настраиваем ChatGPT
model_name = "gpt-3.5-turbo"

llm = ChatOpenAI(
    openai_api_key=openai_key,
    base_url=model_api_url, model_name=model_name,
    temperature=0.7
    )

# Создание промпта
prompt = PromptTemplate.from_template(prompt_openai_simple_ru)

# Асинхронная функция для генерации текста
async def generate_advertisement(product: str) -> str:
    """Генерирует рекламный текст на основе наименования товара."""
    try:
        # Форматируем промпт с переданным контекстом
        formatted_prompt = prompt.format(product=product)
        logger.info(f"Собранный промпт: {formatted_prompt}")

        # Вызываем модель
        response = await llm.ainvoke(formatted_prompt)

        # Извлекаем текст из объекта AIMessage
        generated_text = response.content
        logger.info(f"Сгенерированный текст: {generated_text}")

        return generated_text
    except Exception as e:
        logger.error(f"Ошибка при генерации текста: {e}")
        return f"Ошибка при генерации текста: {e}"