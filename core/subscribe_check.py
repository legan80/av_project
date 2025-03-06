from core.database import save_user
from core.bot_instance import bot
from core.settings import channel_id
from aiogram.enums import ChatMemberStatus

async def is_subscribed(user_id: int, pool) -> bool:
    """Проверяет, подписан ли пользователь на канал, и обновляет статус в базе."""
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        is_subscriber = member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]

        # Обновляем статус подписки в базе данных
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_subscriber = $1 WHERE user_id = $2",
                is_subscriber, user_id
            )

        return is_subscriber
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False