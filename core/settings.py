from environs import Env

env = Env()  # Создаем экземпляр класса Env
env.read_env()  # Методом read_env() читаем файл .env и загружаем из него переменные в окружение

bot_token = env('BOT_TOKEN')
channel_id = env('CHANNEL_ID')
channel_username = env('CHANNEL_USERNAME')
openai_key = env('OPENAI_KEY')
course_api_key = env('COURSE_API_KEY')
model_api_url = env('MODEL_API_URL')

db = env('DB')
db_address = env('DB_ADDRESS')
db_user = env('DB_USER')
db_pass = env('DB_PASS')