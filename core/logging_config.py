import logging
import sys

def setup_logger():
    """Настройка логирования для всего проекта."""
    # Формат логов
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Базовый уровень логирования
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # Логи в консоль
            # logging.FileHandler("bot.log")      # Логи в файл
        ]
    )

    # Возвращаем логгер
    return logging.getLogger(__name__)