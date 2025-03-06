from aiogram import Bot
from core.settings import channel_id  # ID вашего канала
from core.logging_config import setup_logger

# Настройка логирования
logger = setup_logger()

async def publish_to_channel(bot: Bot, original_url: str, result: str, advertisement: str) -> None:
    """Публикует объявление в канал."""
    try:
        # Формируем сообщение для канала
        message_text = (
            f"<b><a href='{original_url}'>🔗 {result}</a></b>\n\n"  # Заголовок с кликабельной ссылкой
            f"{advertisement}"
        )

        # Отправляем сообщение в канал
        message = await bot.send_message(
            chat_id=channel_id,
            text=message_text,
            parse_mode="HTML"
        )
        logger.info("Сообщение успешно опубликовано в канал.")

        # Возвращаем ID сообщения
        return message.message_id
    except Exception as e:
        logger.error(f"Ошибка при публикации в канал: {e}")