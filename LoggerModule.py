import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename="bot_activity.log",   # файл для логов
    level=logging.INFO,            # уровень логирования
    format="%(asctime)s — %(levelname)s — %(message)s"
)

def log_user_action(user_id: int, message: str):
    """Логирование действий пользователя"""
    logging.info(f"USER {user_id}: {message}")

def log_bot_action(action: str):
    """Логирование действий бота"""
    logging.info(f"BOT: {action}")
