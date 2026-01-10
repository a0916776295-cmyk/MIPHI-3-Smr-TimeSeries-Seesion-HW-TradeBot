#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностика проблем с созданием тестов реальности
"""

import sys
import os
sys.path.append('.')

from datetime import datetime, timedelta
import json

def check_system_status():
    """Проверка всех компонентов системы"""
    print("🔍 ДИАГНОСТИКА СИСТЕМЫ СОЗДАНИЯ ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 60)
    
    # 1. Проверка файлов
    print("\n📁 ПРОВЕРКА ФАЙЛОВ:")
    files_to_check = [
        'FinGolem.py',
        'reality_test.py', 
        'reality_tests.json'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} - найден")
        else:
            print(f"❌ {file} - НЕ НАЙДЕН")
    
    # 2. Проверка модулей
    print("\n🔧 ПРОВЕРКА ИМПОРТОВ:")
    try:
        from reality_test import add_reality_test, get_user_reality_test
        print("✅ reality_test модуль - импортирован")
        
        from datetime import datetime, timedelta
        import pandas as pd
        print("✅ Зависимости - импортированы")
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return
    
    # 3. Проверка файла тестов
    print("\n📊 ПРОВЕРКА БАЗЫ ТЕСТОВ:")
    try:
        if os.path.exists('reality_tests.json'):
            with open('reality_tests.json', 'r', encoding='utf-8') as f:
                tests = json.load(f)
            print(f"✅ Файл тестов найден, {len(tests)} активных тестов")
            
            if tests:
                print("📋 Активные тесты:")
                for user_id, test in tests.items():
                    print(f"   👤 Пользователь {user_id}:")
                    print(f"      📈 Тикер: {test.get('ticker')}")
                    print(f"      📅 Дата: {test.get('target_date')}")
                    print(f"      🤖 Модель: {test.get('model_name')}")
            else:
                print("📋 Нет активных тестов")
        else:
            print("⚠️ Файл reality_tests.json не найден")
    except Exception as e:
        print(f"❌ Ошибка чтения файла тестов: {e}")
    
    # 4. Тест создания
    print("\n🧪 ТЕСТ СОЗДАНИЯ:")
    try:
        test_user_id = 111111
        ticker = 'TEST'
        amount = 100
        model_name = 'DIAGNOSTIC_MODEL'
        test_predictions = [100.0, 101.0, 102.0]
        
        forecast_dates = pd.date_range(
            start=datetime.now().date(),
            periods=3,
            freq='D'
        ).strftime('%Y-%m-%d').tolist()
        
        test_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        success = add_reality_test(
            test_user_id, ticker, test_date,
            test_predictions, forecast_dates,
            amount, model_name
        )
        
        if success:
            print("✅ Создание теста работает")
            
            # Проверяем, что тест сохранился
            saved_test = get_user_reality_test(test_user_id)
            if saved_test:
                print("✅ Сохранение теста работает")
            else:
                print("❌ Проблема с сохранением теста")
            
            # Удаляем тестовый тест
            from reality_test import reality_tests, save_reality_tests
            if test_user_id in reality_tests:
                del reality_tests[test_user_id]
                save_reality_tests()
                print("🗑️ Диагностический тест удален")
        else:
            print("❌ Создание теста НЕ РАБОТАЕТ")
            
    except Exception as e:
        print(f"❌ Ошибка в тесте создания: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Проверка процессов
    print("\n🔄 ПРОВЕРКА ПРОЦЕССОВ:")
    try:
        import psutil
        
        # Ищем процессы Python
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any('FinGolem.py' in cmd for cmd in cmdline):
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': ' '.join(cmdline)
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            print(f"✅ Найдено {len(python_processes)} процессов FinGolem:")
            for proc in python_processes:
                print(f"   PID {proc['pid']}: {proc['cmdline'][:100]}...")
        else:
            print("⚠️ Процессы FinGolem.py НЕ НАЙДЕНЫ")
            print("💡 Возможно бот не запущен?")
            
    except ImportError:
        print("⚠️ psutil не установлен, не могу проверить процессы")
    except Exception as e:
        print(f"❌ Ошибка проверки процессов: {e}")
    
    # 6. Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ ПО РЕШЕНИЮ ПРОБЛЕМ:")
    print("1. Убедитесь, что бот FinGolem.py запущен")
    print("2. Проверьте, что выполнен полный анализ акций (есть temp_forecast)")
    print("3. Используйте команду /status в боте для диагностики")
    print("4. Проверьте логи бота на ошибки")
    print("5. При необходимости перезапустите бота")

if __name__ == "__main__":
    check_system_status()