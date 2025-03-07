import asyncpg
from core.settings import db, db_address, db_user, db_pass  # URL базы данных (например, postgres://user:password@localhost:5432/avito_db)
from core.logging_config import setup_logger

logger = setup_logger()

# Формируем строку подключения
DATABASE_CONN = f'postgres://{db_user}:{db_pass}@{db_address}/{db}'

async def create_pool():
    """Создаёт пул подключений к базе данных."""
    return await asyncpg.create_pool(DATABASE_CONN)

async def save_user(conn, user_id: int, name: str, username: str, phone: str = None, birth_date: str = None, is_subscriber: bool = False):
    """Сохраняет данные пользователя в таблицу users."""
    query = """
    INSERT INTO users (user_id, name, username, phone, birth_date, is_subscriber, created_at)
    VALUES ($1, $2, $3, $4, $5, $6, NOW() AT TIME ZONE 'UTC')
    ON CONFLICT (user_id) DO UPDATE SET
        name = EXCLUDED.name,
        username = EXCLUDED.username,
        phone = EXCLUDED.phone,
        birth_date = EXCLUDED.birth_date,
        is_subscriber = EXCLUDED.is_subscriber;
    """
    await conn.execute(query, user_id, name, username, phone, birth_date, is_subscriber)

async def save_request(conn, user_id: int, message_text: str, parsed_title: str, parsed_category: str, generated_text: str):
    """Сохраняет данные запроса в таблицу requests."""
    query = """
    INSERT INTO requests (user_id, message_text, parsed_title, parsed_category, generated_text, created_at)
    VALUES ($1, $2, $3, $4, $5, NOW() AT TIME ZONE 'UTC');
    """
    await conn.execute(query, user_id, message_text, parsed_title, parsed_category, generated_text)

async def is_duplicate_url(conn, url: str) -> bool:
    """
    Проверяет, есть ли такая ссылка среди последних 10 запросов в базе.
    Возвращает True, если ссылка уже была, иначе False.
    """
    query = """
    SELECT EXISTS (
        SELECT 1
        FROM requests
        WHERE message_text = $1
        ORDER BY created_at DESC
        LIMIT 10
    );
    """
    return await conn.fetchval(query, url)