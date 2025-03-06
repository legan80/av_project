from core.bot_instance import bot
from core.settings import channel_username
from core.llm import generate_advertisement
from core.logging_config import setup_logger

from core.keyboards.menu import set_main_menu
from core.subscribe_check import is_subscribed
from core.parser import is_valid_avito_url, parse_avito
from core.channel import publish_to_channel
from core.database import create_pool, save_user, save_request
from lexicon.lexicon_ru import start_text_ru, help_text_ru, wrong_link_text_ru

import re
from aiogram import Dispatcher, types
from aiogram.methods import DeleteMessage
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логирования
logger = setup_logger()

# Глобальная переменная для пула (временное решение)
pool = None

# Создаём диспетчер
dp = Dispatcher()

# Настраиваем кнопку Menu
@dp.startup()
async def main():
    await set_main_menu(bot)

# Команда /start
@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    # Сохраняем пользователя в базу данных
    async with pool.acquire() as conn:
        await save_user(conn, user_id=user_id, name=name, username=username)

    # Проверяем подписку
    if await is_subscribed(user_id, pool):
        await message.answer(
            text=start_text_ru)
    else:
        # Если пользователь не подписан, показываем кнопку с предложением подписаться
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Подписаться на канал",
            url="https://t.me/avito_prodano"  # Замените на ссылку на ваш канал
        ))
        builder.add(types.InlineKeyboardButton(
            text="Я подписался",
            callback_data="check_subscription"
        ))

        await message.answer(
            "Пожалуйста, подпишитесь на наш канал, чтобы продолжить использование бота.",
            reply_markup=builder.as_markup()
        )


# Обработка нажатия кнопки "Я подписался"
@dp.callback_query(lambda callback: callback.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Повторная проверка подписки
    if await is_subscribed(user_id, pool):
        await callback.message.edit_text("Спасибо за подписку! Теперь вы можете пользоваться ботом.")
    else:
        await callback.answer("Вы ещё не подписались на канал.", show_alert=True)

# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        text=help_text_ru,
        parse_mode="HTML"  # Указываем режим разметки
    )

# Регулярное выражение для проверки ссылок Avito
AVITO_URL_PATTERN = re.compile(r'https://(www\.|m\.)?avito\.ru/[^/]+/[^/]+/.+')

# Хэндлер для обработки ссылок
@dp.message(lambda message: AVITO_URL_PATTERN.search(message.text))
async def handle_avito_link(message: Message):
    user_id = message.from_user.id

    # Логируем значение channel_username
    logger.info(f"channel_username: {channel_username}")

    # Проверяем подписку пользователя на канал
    if not await is_subscribed(user_id, pool):
        # Если пользователь не подписан, показываем кнопку с предложением подписаться
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Подписаться на канал",
            url=f"https://t.me/{channel_username}"  # Замените на ссылку на ваш канал
        ))
        builder.add(types.InlineKeyboardButton(
            text="Я подписался",
            callback_data="check_subscription"
        ))

        await message.answer(
            "Пожалуйста, подпишитесь на наш канал, чтобы начать использование бота.",
            reply_markup=builder.as_markup()
        )
        return

    # Ищем ссылку в тексте сообщения
    match = AVITO_URL_PATTERN.search(message.text)
    if not match:
        await message.answer(text=wrong_link_text_ru)
        return

    # Извлекаем ссылку
    url = match.group(0)
    logger.info(f"Извлечённая ссылка: {url}")

    # Проверяем корректность ссылки
    if not is_valid_avito_url(url):
        logger.warning(f"Некорректная ссылка: {url}")
        await message.answer(text=wrong_link_text_ru)
        return

    # Отправляем промежуточное сообщение
    processing_message = await message.answer("Ссылка принята. Обрабатываю...")

    # Парсим данные
    result, category = await parse_avito(url)
    logger.info(f"Результат парсинга: {result}")

    # Генерируем рекламный текст
    advertisement = await generate_advertisement(result)
    logger.info(f"Сгенерированный текст: {advertisement}")

    # Сохраняем запрос в базу данных
    async with pool.acquire() as conn:
        await save_request(
            conn,
            user_id=user_id,
            message_text=url,
            parsed_title=result,
            parsed_category=category,
            generated_text=advertisement
        )

    # Удаляем промежуточное сообщение
    await bot(DeleteMessage(chat_id=message.chat.id, message_id=processing_message.message_id))

    # Формируем финальное сообщение
    final_message = (
        f"<b>{result}</b>\n"
        f"{advertisement}"
    )

    # Отправляем результат генерации ответом на ссылку
    await message.reply(final_message, parse_mode="HTML")

    # Публикуем объявление в канал и получаем ID сообщения
    message_id = await publish_to_channel(bot, url, result, advertisement)

    # Если публикация успешна, отправляем пользователю ссылку на объявление
    if message_id:
        # Формируем ссылку на сообщение в канале
        channel_link = f"https://t.me/{channel_username}/{message_id}"

        # Отправляем пользователю сообщение с ссылкой
        await message.answer(
            # Заголовок с кликабельной ссылкой
            f"<b><a href='{channel_link}'>🔗 Ваше объявление</a></b> опубликовано в канале @avito_prodano.\n🎉 Будьте первым, кто поставит реакцию!\n\n",
            parse_mode="HTML"
        )

# Проверяем корректность ссылки
@dp.message(lambda message: message.text.startswith(('http')))
async def wrong_avito_link(message: Message):
    await message.answer(text=wrong_link_text_ru)
    return

# Запуск бота
async def main():
    global pool
    # Создаём пул подключений к базе данных
    pool = await create_pool()

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())