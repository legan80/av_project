-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    name TEXT,
    username TEXT,
    phone TEXT,
    birth_date DATE,
    is_subscriber BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы requests
CREATE TABLE IF NOT EXISTS requests (
    request_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    message_text TEXT,
    parsed_title TEXT,
    parsed_category TEXT,
    generated_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание пользователя avitobot (если его нет)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'avitobot') THEN
        CREATE USER avitobot WITH PASSWORD 'ваш_пароль';
    END IF;
END $$;

-- Предоставление прав пользователю avitobot
GRANT ALL PRIVILEGES ON TABLE users TO avitobot;
GRANT ALL PRIVILEGES ON TABLE requests TO avitobot;
GRANT USAGE, SELECT ON SEQUENCE requests_request_id_seq TO avitobot;