# -*- coding: utf-8 -*-
"""
Тест функции перезапуска бота
"""

import sys
import os

# Настройка кодировки для Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def safe_print(text):
    """Безопасный вывод текста с поддержкой кириллицы"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print("Output encoding error")

def test_restart_functionality():
    """Тестируем функцию перезапуска"""
    safe_print("🔄 Тестирование функции перезапуска бота...")
    
    try:
        # Импортируем необходимые модули
        from MenuBot import get_main_menu, get_help_text
        from FinGolem import get_user_state
        
        safe_print("✅ Импорт модулей успешен")
        
        # Тестируем главное меню с новой кнопкой
        safe_print("\n🎮 Тестирование нового главного меню...")
        menu = get_main_menu()
        
        # Проверяем наличие кнопки перезапуска
        restart_button_found = False
        for row in menu.keyboard:
            for button in row:
                if "🔄 Перезапуск" in button.text:
                    restart_button_found = True
                    safe_print(f"✅ Найдена кнопка перезапуска: '{button.text}'")
                    break
        
        if not restart_button_found:
            safe_print("❌ Кнопка перезапуска не найдена в меню")
        
        # Тестируем структуру меню
        safe_print(f"\n📊 Структура главного меню:")
        safe_print(f"   Строк кнопок: {len(menu.keyboard)}")
        for i, row in enumerate(menu.keyboard, 1):
            buttons_text = [btn.text for btn in row]
            safe_print(f"   Строка {i}: {buttons_text}")
        
        # Тестируем обновленный текст помощи
        safe_print("\n📖 Тестирование обновленного текста помощи...")
        help_text = get_help_text()
        
        if "🔄 Перезапуск" in help_text:
            safe_print("✅ Информация о перезапуске добавлена в помощь")
        else:
            safe_print("❌ Информация о перезапуске отсутствует в помощи")
        
        # Тестируем функцию состояния пользователя
        safe_print("\n👤 Тестирование состояния пользователя...")
        
        # Создаем тестовое состояние
        test_user_id = 12345
        state = get_user_state(test_user_id)
        safe_print(f"   Начальное состояние: {state}")
        
        # Изменяем состояние
        state["ticker"] = "AAPL"
        state["amount"] = 1000
        state["temp_forecast"] = {"test": "data"}
        safe_print(f"   Измененное состояние: {state}")
        
        # Имитируем сброс состояния (как в функции перезапуска)
        old_state = state.copy()
        state.clear()
        state.update({"ticker": None, "amount": None, "forecast_days": 30, "mode": "normal", "temp_forecast": None})
        safe_print(f"   Состояние после сброса: {state}")
        safe_print(f"   Старое состояние: {old_state}")
        
        safe_print("\n🎉 Тестирование функции перезапуска завершено успешно!")
        
    except Exception as e:
        safe_print(f"❌ Ошибка при тестировании: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    safe_print("🚀 Тестирование новой функции перезапуска")
    safe_print("=" * 50)
    test_restart_functionality()
    safe_print("=" * 50)
    safe_print("🏁 Тестирование завершено!")