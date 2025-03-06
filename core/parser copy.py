import asyncio
import aiohttp
import re
import requests
import fake_useragent
import ssl
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для проверки корректности ссылки Avito
def is_valid_avito_url(url: str) -> bool:
    """Проверяет, является ли ссылка корректной ссылкой на объявление Avito."""
    pattern = re.compile(r'^https://www\.avito\.ru/[^/]+/[^/]+/.+$')
    return bool(pattern.match(url))

# Функция для парсинга данных с Avito
async def parse_avito(url: str) -> str:
    """Парсит данные с Avito и возвращает наименование товара."""
    try:
        # Запускаем Playwright
        async with async_playwright() as p:
            # Запускаем браузер (например, Chromium)
            browser = await p.chromium.launch(headless=False)  # headless=False для отладки
            page = await browser.new_page()

            # Устанавливаем заголовки
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Referer": "https://www.avito.ru/",
            }
            await page.set_extra_http_headers(headers)

            # Переходим на страницу
            await page.goto(url)

            # Ждём появления заголовка (увеличиваем таймаут до 30 секунд)
            try:
                await page.wait_for_selector('h1[data-marker="item-view/title-info"]', timeout=30000)
            except Exception as e:
                logger.error(f"Элемент не найден: {e}")
                return "Элемент с наименованием товара не найден"

            # Получаем содержимое страницы
            content = await page.content()

            # Закрываем браузер
            await browser.close()

        # Парсим HTML с использованием html.parser
        soup = BeautifulSoup(content, 'html.parser')

        # Извлекаем наименование товара
        try:
            # Поиск по атрибуту data-marker
            name_tag = soup.find('h1', {'data-marker': 'item-view/title-info'})
            if not name_tag:
                # Если не найдено, ищем по классу
                name_tag = soup.find('h1', class_='styles-module-root-W_crH')

            if name_tag:
                name = name_tag.text.strip()
            else:
                logger.error("Элемент с наименованием товара не найден")
                return "Элемент с наименованием товара не найден"
        except AttributeError as e:
            logger.error(f"Ошибка при извлечении наименования товара: {e}")
            return f"Ошибка при извлечении наименования товара: {e}"

        logger.info(f"Успешно обработана ссылка: {url}")
        return f"Наименование товара: {name}"

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return f"Неожиданная ошибка: {e}"