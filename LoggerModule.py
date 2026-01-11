import logging
import os
from datetime import datetime

# Создаем папку Log если её нет
log_dir = "Log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка единого логгера
log_file = os.path.join(log_dir, 'bot_activity.txt')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s',
    encoding='utf-8'
)

logger = logging.getLogger('FinGolem')

def log_user_action(user_id: int, message: str):
    """Логирование действий пользователя"""
    logger.info(f"[USER {user_id}] {message}")

def log_bot_action(action: str):
    """Логирование действий бота"""
    logger.info(f"[BOT] {action}")

def log_error(module: str, user_id: int, error_message: str, traceback_info: str = None):
    """Логирование ошибок"""
    logger.error(f"[ERROR] [{module}] [USER {user_id}] {error_message}")
    if traceback_info:
        logger.error(f"[ERROR] [{module}] [USER {user_id}] TRACEBACK: {traceback_info}")

def log_trading_operation(user_id: int, ticker: str, operation: str, 
                         amount: str, price: str, reason: str):
    """Логирование торговых операций"""
    logger.info(f"[TRADE] [USER {user_id}] {ticker} {operation} {amount} {price} {reason}")

def log_analysis_result(user_id: int, ticker: str, profit: str):
    """Логирование результатов анализа"""
    logger.info(f"[ANALYSIS] [USER {user_id}] {ticker} {profit}")

def log_model_performance(model_name: str, ticker: str, execution_time: float, 
                         accuracy: float = None, rmse: float = None):
    """Логирование производительности моделей"""
    metrics = []
    if execution_time:
        metrics.append(f"Time:{execution_time:.2f}s")
    if accuracy:
        metrics.append(f"Accuracy:{accuracy:.1f}%")
    if rmse:
        metrics.append(f"RMSE:{rmse:.2f}")
    
    logger.info(f"[PERF] {model_name} {ticker} {' '.join(metrics)}")

def log_system_start():
    """Логирование запуска системы"""
    logger.info("=" * 50)
    logger.info("🚀 FinGolem Trading Bot STARTED")
    logger.info("=" * 50)

def log_system_stop():
    """Логирование остановки системы"""
    logger.info("🛑 FinGolem Trading Bot STOPPED")
    logger.info("=" * 50)
