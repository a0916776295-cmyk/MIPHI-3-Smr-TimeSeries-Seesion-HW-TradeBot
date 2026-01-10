#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import config_bot
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import Model_Prophet, Model_ARIMA, Model_LSTM, Model_XGBoost, Model_Ridge, Model_RandomForest
import Model_SARIMA, Model_GRU, Model_CatBoost, Model_TFT
import Model_LSTM_optimized, Model_GRU_optimized  
import Model_Transformer, Model_Informer, Model_Ensemble
import FinGolem
import trading_recommendations
import reality_test
import graph
import finance

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_debug.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class UserStates(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_days = State()
    waiting_for_test_date = State()

# Храним временные данные пользователей
user_data = {}

# Инициализация бота и диспетчера
bot = Bot(token=config_bot.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer(
        "🤖 Добро пожаловать в FinGolem!\n\n"
        "Я помогу вам анализировать акции и строить прогнозы.\n\n"
        "📊 Напишите тикер акции (например, AAPL, GOOGL, TSLA)\n"
        "или используйте команды:\n"
        "/help - помощь\n"
        "/status - статус системы\n"
        "/test_reality - тест механизма реальности"
    )

@dp.message(Command("help"))
async def send_help(message: types.Message):
    help_text = """
🤖 **FinGolem - Помощник по анализу акций**

📋 **Основные команды:**
/start - Запуск бота
/help - Эта справка
/status - Проверить статус системы
/test_reality - Протестировать механизм реальности

📊 **Как использовать:**
1. Напишите тикер акции (AAPL, GOOGL, TSLA, etc.)
2. Укажите количество дней для загрузки данных
3. Получите анализ и прогноз
4. При необходимости создайте тест реальности

🎯 **Поддерживаемые модели:**
• Prophet, ARIMA, SARIMA
• LSTM, GRU (обычные и оптимизированные)  
• XGBoost, CatBoost, Random Forest
• Transformer, Informer
• Ensemble методы
• Ridge Regression, TFT

💡 **Фишки:**
• Автоматические торговые рекомендации
• Тесты реальности прогнозов
• Расчет потенциальной прибыли
• Графики и визуализация
    """
    await message.answer(help_text, parse_mode="Markdown")

@dp.message(Command("status"))
async def check_status(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запросил статус")
    
    status_text = "🔍 **СТАТУС СИСТЕМЫ**\n\n"
    
    # Проверка модулей
    modules_status = []
    try:
        import Model_Prophet
        modules_status.append("✅ Prophet")
    except:
        modules_status.append("❌ Prophet")
        
    try:
        import Model_Transformer  
        modules_status.append("✅ Transformer")
    except:
        modules_status.append("❌ Transformer")
        
    try:
        import reality_test
        modules_status.append("✅ Reality Test")
    except:
        modules_status.append("❌ Reality Test")
    
    status_text += "📦 **Модули:**\n" + "\n".join(modules_status) + "\n\n"
    
    # Проверка файлов
    files_status = []
    files_to_check = ['reality_tests.json', 'temp_forecast']
    for file_name in files_to_check:
        if os.path.exists(file_name):
            files_status.append(f"✅ {file_name}")
        else:
            files_status.append(f"❌ {file_name}")
    
    status_text += "📁 **Файлы:**\n" + "\n".join(files_status) + "\n\n"
    
    # Проверка активных тестов
    try:
        tests = reality_test.load_reality_tests()
        if tests:
            status_text += f"🧪 **Активных тестов:** {len(tests)}\n"
            for test in tests:
                status_text += f"   👤 Пользователь {test['user_id']}: {test['ticker']}\n"
        else:
            status_text += "🧪 **Активных тестов:** 0\n"
    except Exception as e:
        status_text += f"🧪 **Ошибка загрузки тестов:** {e}\n"
    
    status_text += "\n✅ **Бот работает нормально**"
    
    await message.answer(status_text, parse_mode="Markdown")

async def main():
    logger.info("🚀 Запуск FinGolem...")
    
    try:
        # Проверка подключения
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот подключен: {bot_info.username}")
        
        # Запуск опроса
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise

if __name__ == '__main__':
    print("🤖 Запуск FinGolem в отладочном режиме...")
    asyncio.run(main())