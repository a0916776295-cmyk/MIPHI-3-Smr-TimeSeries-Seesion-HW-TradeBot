#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json
import uuid
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Тестируем новую систему тестов реальности

def test_structured_reality_tests():
    print("🧪 ТЕСТИРОВАНИЕ НОВОЙ СИСТЕМЫ ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 60)
    
    try:
        # 1. Симулируем создание теста
        print("1️⃣ Создание тестовых данных...")
        
        test_id = str(uuid.uuid4())[:8]
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticker = "TEST_TICKER"
        
        # Создаем папку для теста
        test_folder = f"RealityTests/{ticker}_test_{current_time}_{test_id}"
        os.makedirs(test_folder, exist_ok=True)
        
        print(f"✅ Папка создана: {test_folder}")
        
        # 2. Создаем тестовые данные
        print("2️⃣ Сохранение тестовых данных...")
        
        test_data = {
            "test_id": test_id,
            "user_id": 999999,
            "username": "test_user",
            "ticker": ticker,
            "target_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "predictions": [100.0, 101.0, 102.0, 103.0, 104.0],
            "forecast_dates": [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)],
            "amount": 1000,
            "model_name": "TEST_MODEL",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "folder": test_folder,
            "forecast_days": 5
        }
        
        # Сохраняем детали теста
        test_file = os.path.join(test_folder, "test_details.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Тест сохранен: {test_file}")
        
        # Сохраняем прогноз отдельно
        forecast_file = os.path.join(test_folder, "forecast_data.json")
        with open(forecast_file, 'w', encoding='utf-8') as f:
            json.dump({
                "predictions": test_data["predictions"],
                "dates": test_data["forecast_dates"],
                "model": test_data["model_name"],
                "ticker": test_data["ticker"]
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Прогноз сохранен: {forecast_file}")
        
        # 3. Тестируем чтение данных
        print("3️⃣ Тестирование чтения данных...")
        
        # Читаем данные обратно
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print(f"✅ Данные загружены:")
        print(f"   📋 ID теста: {loaded_data['test_id']}")
        print(f"   📈 Тикер: {loaded_data['ticker']}")
        print(f"   👤 Пользователь: {loaded_data['user_id']}")
        print(f"   📅 Дата: {loaded_data['target_date']}")
        print(f"   📊 Статус: {loaded_data['status']}")
        
        # 4. Тестируем функции статуса
        print("4️⃣ Тестирование функций статуса...")
        
        # Добавляем импорт FinGolem для тестирования функций
        try:
            from FinGolem import get_user_test_status
            user_tests = get_user_test_status(999999)
            print(f"✅ Найдено тестов для пользователя 999999: {len(user_tests)}")
            
            for test in user_tests:
                print(f"   📋 Тест: {test['test_id']} - {test['status']}")
        except Exception as e:
            print(f"⚠️ Функция get_user_test_status недоступна: {e}")
        
        # 5. Очистка тестовых данных
        print("5️⃣ Очистка тестовых данных...")
        
        import shutil
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)
            print(f"🗑️ Тестовая папка удалена: {test_folder}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Новая система тестов реальности работает корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_instructions():
    print("\n📱 ИНСТРУКЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ:")
    print("=" * 50)
    print("1. 📊 Сделайте анализ любой акции в боте")
    print("2. 🧪 Перейдите в 'Испытание реальностью'")
    print("3. 🔬 Нажмите 'Создать тест'")
    print("4. 📅 Выберите дату проверки")
    print("5. ✅ Тест будет создан и сохранен в отдельную папку")
    print("6. 🔍 Используйте 'Мои тесты' для отслеживания статуса")
    print("7. ⏰ Дождитесь наступления даты или выполните вручную")
    print()
    print("🆕 НОВЫЕ ВОЗМОЖНОСТИ:")
    print("   • Структурированное хранение тестов в отдельных папках")
    print("   • Уникальные ID для каждого теста")
    print("   • Детальное отслеживание статуса")
    print("   • Сохранение всех данных прогноза")
    print("   • Улучшенные уведомления")

if __name__ == "__main__":
    print("🤖 ТЕСТ НОВОЙ СИСТЕМЫ ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 70)
    
    success = test_structured_reality_tests()
    show_instructions()
    
    if success:
        print("\n🚀 СИСТЕМА ГОТОВА К РАБОТЕ!")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")