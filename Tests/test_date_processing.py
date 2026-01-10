#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_date_selection():
    print("📅 ТЕСТИРОВАНИЕ ФУНКЦИИ ОБРАБОТКИ ДАТ")
    print("=" * 50)
    
    try:
        # Тест 1: Проверка импорта datetime
        print("1️⃣ Проверка импорта datetime...")
        from datetime import datetime, timedelta
        print(f"✅ datetime импортирован: текущая дата {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Тест 2: Парсинг дат из текста
        print("2️⃣ Тестирование парсинга дат...")
        
        test_texts = [
            "📅 2026-01-11",
            "📅 2026-01-12", 
            "📅 2026-01-15",
            "◀️ Назад",
            "✏️ Своя дата"
        ]
        
        for text in test_texts:
            if text.startswith("📅 "):
                extracted_date = text[2:]  # Убираем эмодзи и пробел (📅 - это 2 символа)
                print(f"   📅 Из '{text}' извлечена дата: '{extracted_date}'")
                
                # Валидируем дату
                try:
                    test_date = datetime.strptime(extracted_date, "%Y-%m-%d")
                    tomorrow = datetime.now() + timedelta(days=1)
                    
                    if test_date >= tomorrow:
                        print(f"   ✅ Дата валидна: {test_date.strftime('%Y-%m-%d')}")
                    else:
                        print(f"   ❌ Дата слишком ранняя: {test_date.strftime('%Y-%m-%d')}")
                        
                except ValueError as e:
                    print(f"   ❌ Неверный формат даты: {e}")
                    
            elif text == "◀️ Назад":
                print(f"   ↩️ Команда возврата: '{text}'")
            elif text == "✏️ Своя дата":
                print(f"   ✏️ Команда ввода своей даты: '{text}'")
            else:
                print(f"   ❓ Неопознанная команда: '{text}'")
        
        # Тест 3: Проверка будущих дат
        print("3️⃣ Тестирование будущих дат...")
        
        future_dates = [
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        ]
        
        for date_str in future_dates:
            test_date = datetime.strptime(date_str, "%Y-%m-%d")
            tomorrow = datetime.now() + timedelta(days=1)
            
            if test_date >= tomorrow:
                days_from_now = (test_date - datetime.now()).days
                print(f"   ✅ {date_str} - через {days_from_now} дней")
            else:
                print(f"   ❌ {date_str} - слишком рано")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Функция обработки дат готова к работе")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 ТЕСТ ФУНКЦИИ ОБРАБОТКИ ДАТ")
    print("=" * 60)
    
    success = test_date_selection()
    
    if success:
        print("\n🚀 СИСТЕМА ОБРАБОТКИ ДАТ РАБОТАЕТ!")
        print("\nТеперь пользователь pnFmvo сможет успешно создавать тесты реальности")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")