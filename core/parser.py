from core.logging_config import setup_logger

import aiohttp
import re
from bs4 import BeautifulSoup

# Настройка логирования
logger = setup_logger()

# Список стоп-слов для обрезки
STOP_WORDS = [
    # 'купить',
    'авито',
    # 'работа',
    # 'снять'
     ]

def clean_title(title: str) -> tuple[str, str]:
    """
    Очищает заголовок от стоп-слов, но оставляет категорию.
    Возвращает кортеж: (очищенный заголовок с категорией, категория).
    """
    logger.info(f"Принят в обработку title: {title}")

    # Извлекаем категорию (она между двумя |)
    category_match = re.search(r'\|\s*(.*?)\s*\|', title)
    category = category_match.group(1).strip() if category_match else ""

    # Заменяем символ "|" на запятую
    title = re.sub(r'\s*\|\s*', ', ', title)

    # Приводим заголовок к нижнему регистру для регистронезависимого поиска
    title_lower = title.lower()

    # Поиск самого раннего вхождения любого стоп-слова
    min_index = len(title)  # Максимальное значение по умолчанию
    for stop_word in STOP_WORDS:
        index = title_lower.find(stop_word.lower())
        if index != -1 and index < min_index:
            min_index = index

    # Если нашли стоп-слово, обрезаем заголовок
    if min_index < len(title):
        title = title[:min_index].strip()

    # Удаляем лишние символы (например, запятые, тире)
    title = re.sub(r'[,-]\s*$', '', title).strip()

    logger.info(f"Результат парсинга: заголовок={title}, категория={category}")
    return title, category

# Функция для проверки корректности ссылки Avito
def is_valid_avito_url(url: str) -> bool:
    """Проверяет, является ли ссылка корректной ссылкой на объявление Avito."""
    # pattern = re.compile(r'^https://www\.avito\.ru/[^/]+/[^/]+/.+$')
    pattern = re.compile(r'^https://(www\.|m\.)?avito\.ru/[^/]+/[^/]+/.+$')
    return bool(pattern.match(url))

async def parse_avito(url: str) -> tuple[str, str]:
    """
    Парсит данные с Avito и возвращает кортеж:
    - очищенный заголовок,
    - категория.
    """
    try:
        # Если ссылка мобильная, заменяем её на десктопную
        if url.startswith("https://m.avito.ru"):
            url = url.replace("https://m.avito.ru", "https://www.avito.ru")

        # Заголовки для запроса
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://www.avito.ru/",
        }

        # Выполняем асинхронный запрос
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Проверяем, что запрос успешен
                html = await response.text()

        # Парсим HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Извлекаем содержимое тега <title>
        title = soup.title.string

        # Очищаем заголовок и извлекаем категорию
        cleaned_title, category = clean_title(title)

        # Возвращаем результат
        logger.info(f"Успешно обработана ссылка: {url}")
        return cleaned_title, category

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return f"Неожиданная ошибка: {e}", ""