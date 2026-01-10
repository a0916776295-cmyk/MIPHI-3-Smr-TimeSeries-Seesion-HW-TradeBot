#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import reality_test
import numpy as np
from datetime import datetime, timedelta

def test_reality_test_creation():
    print("🔍 ТЕСТИРОВАНИЕ СОЗДАНИЯ ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 50)
    
    # Параметры теста
    test_user_id = 999999
    test_ticker = "AAPL" 
    test_date = datetime.now() + timedelta(days=5)
    test_model = "LSTM"
    test_amount = 1000
    test_prediction = 150.0
    
    print(f"👤 Пользователь: {test_user_id}")
    print(f"📈 Тикер: {test_ticker}")
    print(f"📅 Дата тестирования: {test_date.strftime('%Y-%m-%d')}")
    print(f"🤖 Модель: {test_model}")
    print(f"💰 Сумма: {test_amount}")
    print(f"📊 Прогноз: {test_prediction}")
    print()
    
    try:
        # 1. Загружаем существующие тесты
        print("1️⃣ Загрузка существующих тестов...")
        reality_test.load_reality_tests()
        tests = reality_test.get_all_user_tests()
        print(f"   📋 Найдено {len(tests)} существующих тестов")
        
        # 2. Добавляем новый тест
        print("2️⃣ Добавление нового теста...")
        result = reality_test.add_reality_test(
            test_user_id, 
            test_ticker, 
            test_date.strftime('%Y-%m-%d'), 
            np.array([test_prediction]),  # Нужен numpy array
            [test_date.strftime('%Y-%m-%d')], 
            test_amount,
            test_model
        )
        
        if result:
            print("   ✅ Тест успешно добавлен")
        else:
            print("   ❌ Ошибка при добавлении теста")
            return False
            
        # 3. Проверяем, что тест добавился
        print("3️⃣ Проверка добавления...")
        updated_tests = reality_test.get_all_user_tests()
        print(f"   📋 Теперь тестов: {len(updated_tests)}")
        
        # Ищем наш тест
        our_test = updated_tests.get(test_user_id)
        if our_test and our_test['ticker'] == test_ticker:
            print("   ✅ Тест найден в базе")
            print(f"      📊 Прогноз: {our_test.get('forecast', 'не указан')}")
            print(f"      💰 Сумма: {our_test.get('amount', 'не указана')}")
        else:
            print("   ❌ Тест НЕ найден в базе")
            return False
            
        # 4. Очищаем тестовые данные
        print("4️⃣ Очистка тестовых данных...")
        reality_test.reality_tests = {k: v for k, v in reality_test.reality_tests.items() 
                                     if not (k == test_user_id and v['ticker'] == test_ticker)}
        reality_test.save_reality_tests()
        print("   🗑️ Тестовые данные удалены")
        
        print()
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Механизм создания тестов реальности работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_instructions():
    print()
    print("📋 ИНСТРУКЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ:")
    print("=" * 50)
    print("1. 🤖 Убедитесь, что бот FinGolem.py запущен")
    print("2. 📊 Проведите анализ любой акции (например, AAPL)")
    print("3. 📅 Дождитесь предложения создать тест реальности")
    print("4. 🗓️ Выберите дату в будущем")
    print("5. ✅ Тест должен быть создан автоматически")
    print()
    print("🔍 Если проблемы продолжаются:")
    print("   • Используйте команду /status в боте")
    print("   • Проверьте, что есть temp_forecast после анализа")
    print("   • Перезапустите бота командой: python FinGolem.py")

if __name__ == "__main__":
    print("🤖 ДИАГНОСТИКА СИСТЕМЫ ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 60)
    
    success = test_reality_test_creation()
    show_instructions()
    
    if success:
        print("\n🚀 СИСТЕМА РАБОТАЕТ КОРРЕКТНО!")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")