from aiogram import Bot
from core.settings import bot_token
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

# Инициализация бота
bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))