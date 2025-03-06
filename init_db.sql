-- Создание таблицы users
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name TEXT,
    username TEXT,
    phone TEXT,
    birth_date DATE,
    is_subscriber BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()  -- Указываем тип timestamp with time zone
);

-- Создание таблицы requests
CREATE TABLE requests (
    request_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    message_text TEXT,
    parsed_title TEXT,
    parsed_category TEXT,
    generated_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()  -- Указываем тип timestamp with time zone
);

-- Предоставление прав пользователю avitobot
GRANT ALL PRIVILEGES ON TABLE users TO avitobot;
GRANT ALL PRIVILEGES ON TABLE requests TO avitobot;
GRANT USAGE, SELECT ON SEQUENCE requests_request_id_seq TO avitobot;