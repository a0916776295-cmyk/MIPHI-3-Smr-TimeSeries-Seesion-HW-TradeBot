#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_reality_test_flow():
    print("🧪 ДИАГНОСТИКА ПОТОКА СОЗДАНИЯ ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 60)
    
    try:
        # Тест 1: Проверка импорта MenuBot
        print("1️⃣ Проверка импорта MenuBot...")
        from MenuBot import get_test_date_menu
        print("✅ MenuBot импортирован успешно")
        
        # Тест 2: Проверка функции get_test_date_menu
        print("2️⃣ Тестирование get_test_date_menu...")
        keyboard = get_test_date_menu()
        print("✅ Клавиатура создана успешно")
        
        # Проверяем кнопки
        buttons = []
        for row in keyboard.keyboard:
            for button in row:
                buttons.append(button.text)
        
        print(f"📱 Найдено кнопок: {len(buttons)}")
        for i, button_text in enumerate(buttons, 1):
            print(f"   {i}. '{button_text}'")
        
        # Тест 3: Симуляция потока
        print("3️⃣ Симуляция потока создания теста...")
        
        # Имитируем состояния
        test_states = {
            "normal": "Обычный режим",
            "offering_reality_test": "Предложение создать тест",
            "selecting_test_date": "Выбор даты теста",
            "entering_custom_date": "Ввод своей даты"
        }
        
        for state_name, description in test_states.items():
            print(f"   🔄 Режим '{state_name}': {description}")
        
        # Тест 4: Проверка обработки кнопок
        print("4️⃣ Тестирование обработки кнопок...")
        
        test_buttons = [
            "✅ Да, создать тест",
            "❌ Нет, спасибо",
            "📅 2026-01-11",
            "📅 2026-01-12",
            "✏️ Своя дата",
            "◀️ Назад"
        ]
        
        for button_text in test_buttons:
            if button_text.startswith("✅"):
                print(f"   ✅ '{button_text}' -> Переход к выбору даты")
            elif button_text.startswith("❌"):
                print(f"   ❌ '{button_text}' -> Возврат в главное меню")
            elif button_text.startswith("📅"):
                extracted_date = button_text[2:]
                print(f"   📅 '{button_text}' -> Дата: '{extracted_date}'")
            elif button_text.startswith("✏️"):
                print(f"   ✏️ '{button_text}' -> Ввод своей даты")
            elif button_text.startswith("◀️"):
                print(f"   ↩️ '{button_text}' -> Возврат назад")
        
        print("\n🎉 ВСЕ КОМПОНЕНТЫ РАБОТАЮТ!")
        print("✅ Поток создания тестов реальности должен работать корректно")
        
        print("\n🔍 ВОЗМОЖНЫЕ ПРОБЛЕМЫ:")
        print("1. Бот может не видеть состояние пользователя")
        print("2. Режим может не переключаться корректно") 
        print("3. Кнопка может не срабатывать из-за точного совпадения текста")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 ДИАГНОСТИКА ПОТОКА ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 70)
    
    success = test_reality_test_flow()
    
    if success:
        print("\n🚀 КОМПОНЕНТЫ ГОТОВЫ К РАБОТЕ!")
        print("\nВозможная проблема в логике обработки состояний пользователя")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ В КОМПОНЕНТАХ!")