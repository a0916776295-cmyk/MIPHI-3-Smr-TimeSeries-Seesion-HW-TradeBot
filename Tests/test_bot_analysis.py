#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест работы кнопки анализа в боте
"""

import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

# Добавляем путь к нашим модулям
sys.path.append('.')

async def test_analysis_button():
    """Тестируем обработчик кнопки анализа"""
    print("🧪 Тестируем обработчик кнопки анализа...")
    
    try:
        # Импортируем необходимые модули
        from FinGolem import process_message, safe_print
        
        # Создаем мок объекты
        mock_message = MagicMock()
        mock_message.text = "📈 Анализ"
        mock_message.from_user.id = 12345
        mock_message.from_user.username = "test_user"
        mock_message.answer = AsyncMock()
        mock_message.answer_photo = AsyncMock()
        
        # Настраиваем состояние пользователя
        from FinGolem import user_states
        user_states[12345] = {
            'ticker': 'AAPL',
            'amount': 1000,
            'forecast_days': 7
        }
        
        print("✅ Все импорты успешны")
        print("✅ Мок объекты созданы")
        print("✅ Состояние пользователя настроено")
        
        # Тестируем обработчик
        print("🚀 Запускаем обработчик анализа...")
        start_time = datetime.now()
        
        try:
            await process_message(mock_message)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Обработчик выполнился за {duration:.1f} секунд")
            print(f"📞 Количество вызовов message.answer: {mock_message.answer.call_count}")
            print(f"🖼️ Количество вызовов message.answer_photo: {mock_message.answer_photo.call_count}")
            
            # Показываем все вызовы
            if mock_message.answer.call_args_list:
                print("\n📝 Текстовые сообщения:")
                for i, call in enumerate(mock_message.answer.call_args_list, 1):
                    args, kwargs = call
                    message_text = args[0] if args else kwargs.get('text', 'Unknown')
                    print(f"  {i}. {message_text[:60]}...")
            
            if mock_message.answer_photo.call_args_list:
                print("\n🖼️ Фото сообщения:")
                for i, call in enumerate(mock_message.answer_photo.call_args_list, 1):
                    args, kwargs = call
                    caption = kwargs.get('caption', 'No caption')
                    print(f"  {i}. Фото с подписью: {caption[:60]}...")
            
        except Exception as process_error:
            print(f"❌ Ошибка в process_message: {str(process_error)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Ошибка в тесте: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Главная функция теста"""
    print("🧪 Начало теста кнопки анализа")
    print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    await test_analysis_button()
    
    print("=" * 50)
    print("🏁 Тест завершен")

if __name__ == "__main__":
    asyncio.run(main())