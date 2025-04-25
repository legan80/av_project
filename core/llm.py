from core.settings import openai_key, model_api_url
from core.logging_config import setup_logger
from lexicon.prompts import prompt_openai_simple_ru

import httpx

from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

# Настройка логирования
logger = setup_logger()

# Настраиваем ChatGPT
# model_name = "gpt-3.5-turbo"
model_name = "claude-3-haiku-20240307"
# model_name = "gpt-4o-mini"

llm = ChatOpenAI(
    openai_api_key=openai_key,
    base_url=model_api_url, model_name=model_name,
    max_tokens=4096,
    # temperature=0.7 # gpt-3.5-turbo
    temperature=0.7 # claude-3-haiku-20240307
    # temperature=0.8 # gpt-4o-mini
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

        # Если объект ответа содержит ошибку API, обрабатываем её
        if isinstance(response, dict) and 'error' in response:
            error_message = response['error'].get('message', 'Неизвестная ошибка API')
            logger.error(f"Ошибка API: {error_message}")
            return "Ой, не могу достучаться до Авито.\nПо-моему я сломался 😱\nПожалуйста, попробуйте позже."

        # Если ответ имеет атрибут error (например, AIMessage), это также ошибка
        if hasattr(response, 'error'):
            error_message = response.error.get('message', 'Неизвестная ошибка API')
            logger.error(f"Ошибка API: {error_message}")
            return "Ой, не могу достучаться до Авито.\nПо-моему я сломался 😱\nПожалуйста, попробуйте позже."

        # Извлекаем текст из AIMessage
        generated_text = response.content
        logger.info(f"Сгенерированный текст: {generated_text}")

        return generated_text

    except httpx.HTTPStatusError as e:
        # Обрабатываем ошибки HTTP (например, 400, 500)
        logger.error(f"Ошибка HTTP при запросе к API: {e.response.status_code} - {e.response.text}")
        return "Ой, не могу достучаться до Авито.\nПо-моему я сломался 😱\nПожалуйста, попробуйте позже."

    except Exception as e:
        # Логируем и возвращаем пользователю стандартное сообщение
        logger.error(f"Ошибка при генерации текста: {e}")
        return "Ой, не могу достучаться до Авито.\nПо-моему я сломался 😱\nПожалуйста, попробуйте позже."