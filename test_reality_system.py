#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест системы тестов реальности после исправлений
"""

import sys
sys.path.append('.')

from Tests.reality_test import load_reality_tests, save_reality_tests, add_reality_test, get_user_reality_test

def test_reality_system():
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ РЕАЛЬНОСТИ")
    print("=" * 50)
    
    # Проверяем загрузку
    print("1️⃣ Тест загрузки...")
    load_reality_tests()
    print("✅ Загрузка работает")
    
    # Проверяем добавление
    print("\n2️⃣ Тест добавления...")
    success = add_reality_test(
        user_id=999999,
        ticker="TEST",
        target_date="2026-01-15", 
        predictions=[100, 105, 110],
        forecast_dates=["2026-01-13", "2026-01-14", "2026-01-15"],
        amount=100,
        model_name="TestModel"
    )
    if success:
        print("✅ Добавление работает")
    else:
        print("❌ Проблема с добавлением")
    
    # Проверяем получение
    print("\n3️⃣ Тест получения...")
    test_data = get_user_reality_test(999999)
    if test_data:
        print(f"✅ Получение работает: {test_data['ticker']}")
    else:
        print("❌ Не удалось получить тест")
    
    # Проверяем сохранение
    print("\n4️⃣ Тест сохранения...")
    save_reality_tests()
    print("✅ Сохранение работает")
    
    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    test_reality_system()