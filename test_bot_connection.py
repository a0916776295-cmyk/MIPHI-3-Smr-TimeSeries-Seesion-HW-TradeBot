import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import config_bot

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot():
    bot = Bot(token=config_bot.BOT_TOKEN)
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен: {bot_info.username}")
        print(f"   ID: {bot_info.id}")
        print(f"   Имя: {bot_info.first_name}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        return False
    finally:
        await bot.session.close()

if __name__ == "__main__":
    success = asyncio.run(test_bot())
    if success:
        print("🚀 Можно запускать основного бота")
    else:
        print("⚠️  Проблемы с подключением")