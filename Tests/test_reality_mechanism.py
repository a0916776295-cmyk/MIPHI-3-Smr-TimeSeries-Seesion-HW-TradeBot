#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический тест механизма реальности
Тестирует полный цикл создания и выполнения теста реальности
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Импорты из проекта
from .reality_test import (
    add_reality_test, 
    get_user_reality_test, 
    check_ready_tests, 
    execute_reality_test,
    remove_reality_test,
    reality_tests
)

def test_reality_mechanism():
    """Полное тестирование механизма реальности"""
    print("🧪 АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ МЕХАНИЗМА РЕАЛЬНОСТИ")
    print("=" * 60)
    
    # Тестовые данные
    test_user_id = 999999  # Тестовый ID пользователя
    ticker = "AAPL"
    amount = 1000
    model_name = "TEST_LSTM"
    
    # Убираем старые тесты для чистоты эксперимента
    if test_user_id in reality_tests:
        del reality_tests[test_user_id]
    
    try:
        print("\n🔄 ЭТАП 1: Создание тестовых данных")
        
        # Создаем тестовый прогноз
        test_predictions = [150.0, 151.5, 149.8, 152.2, 150.9]
        print(f"📊 Прогноз: {test_predictions}")
        
        # Создаем даты прогноза
        forecast_dates = pd.date_range(
            start=datetime.now().date(),
            periods=5,
            freq='D'
        ).strftime('%Y-%m-%d').tolist()
        print(f"📅 Даты прогноза: {forecast_dates}")
        
        # Дата для теста (завтра)
        test_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"🎯 Дата теста: {test_date}")
        print("✅ Тестовые данные готовы")
        
        print("\n🔄 ЭТАП 2: Создание теста реальности")
        success = add_reality_test(
            test_user_id,
            ticker,
            test_date,
            test_predictions,
            forecast_dates,
            amount,
            model_name
        )
        
        if success:
            print("✅ Тест реальности создан успешно")
        else:
            print("❌ Ошибка создания теста")
            return False
        
        print("\n🔄 ЭТАП 3: Проверка сохранения")
        saved_test = get_user_reality_test(test_user_id)
        
        if saved_test:
            print("✅ Тест найден в базе данных")
            print(f"   📈 Тикер: {saved_test['ticker']}")
            print(f"   📅 Дата: {saved_test['target_date']}")
            print(f"   🤖 Модель: {saved_test['model_name']}")
            print(f"   💰 Сумма: ${saved_test['amount']}")
            print(f"   📊 Прогнозов: {len(saved_test['forecast'])}")
        else:
            print("❌ Тест не найден в базе")
            return False
        
        print("\n🔄 ЭТАП 4: Симуляция готовности к выполнению")
        # Меняем дату на сегодня для немедленного выполнения
        reality_tests[test_user_id]["target_date"] = datetime.now().strftime("%Y-%m-%d")
        print(f"🕒 Дата теста изменена на: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Проверяем готовые тесты
        ready_tests = check_ready_tests()
        user_ready = [(uid, test) for uid, test in ready_tests if uid == test_user_id]
        
        if user_ready:
            print("✅ Тест готов к выполнению")
        else:
            print("❌ Тест не готов к выполнению")
            return False
        
        print("\n🔄 ЭТАП 5: Выполнение теста")
        uid, test = user_ready[0]
        result = execute_reality_test(uid, test)
        
        if result and "success" in result:
            print("✅ Тест выполнен успешно")
            print(f"📊 Статус: {result['success']}")
            if 'report' in result:
                report_preview = result['report'][:300] + "..." if len(result['report']) > 300 else result['report']
                print(f"📋 Отчет (превью): {report_preview}")
        else:
            print("❌ Ошибка выполнения теста")
            if result:
                print(f"   Детали: {result}")
            return False
        
        print("\n🔄 ЭТАП 6: Очистка тестовых данных")
        cleanup_success = remove_reality_test(test_user_id)
        if cleanup_success:
            print("✅ Тестовые данные удалены")
        else:
            print("⚠️ Проблема с очисткой данных")
        
        print("\n🎉 ВСЕ ЭТАПЫ ТЕСТИРОВАНИЯ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("✅ Механизм создания и выполнения тестов реальности работает корректно")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {str(e)}")
        import traceback
        print(f"Детали: {traceback.format_exc()}")
        
        # Очистка при ошибке
        if test_user_id in reality_tests:
            del reality_tests[test_user_id]
        
        return False

if __name__ == "__main__":
    success = test_reality_mechanism()
    print(f"\n{'='*60}")
    if success:
        print("🏆 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print("💥 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("="*60)