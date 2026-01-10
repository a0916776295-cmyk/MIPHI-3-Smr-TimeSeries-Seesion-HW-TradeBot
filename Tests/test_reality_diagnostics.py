#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностика системы тестов реальности
"""

import json
import os
from datetime import datetime
import sys

# Добавляем путь к нашим модулям
sys.path.append('.')

def check_reality_tests_storage():
    """Проверяем состояние хранилища тестов реальности"""
    print("🔍 ДИАГНОСТИКА ТЕСТОВ РЕАЛЬНОСТИ")
    print("=" * 50)
    
    # Проверяем файл тестов
    test_file = 'reality_tests.json'
    print(f"📁 Проверка файла: {test_file}")
    
    if os.path.exists(test_file):
        print("✅ Файл существует")
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                tests_data = json.load(f)
            
            print(f"📊 Загружено записей: {len(tests_data)}")
            
            if tests_data:
                print("\n📋 Активные тесты:")
                for user_id, test_data in tests_data.items():
                    print(f"  👤 Пользователь {user_id}:")
                    print(f"     📈 Актив: {test_data.get('ticker', 'N/A')}")
                    print(f"     📅 Дата проверки: {test_data.get('target_date', 'N/A')}")
                    print(f"     🤖 Модель: {test_data.get('model_name', 'N/A')}")
                    print(f"     💰 Сумма: ${test_data.get('amount', 'N/A')}")
                    print(f"     🕐 Создан: {test_data.get('created_at', 'N/A')}")
                    print()
            else:
                print("❌ Файл пустой")
                
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка чтения JSON: {str(e)}")
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {str(e)}")
    else:
        print("❌ Файл не существует")
    
    # Проверяем модуль
    print(f"\n🔧 Проверка модуля reality_test:")
    
    try:
        from .reality_test import reality_tests, get_all_user_tests, load_reality_tests
        print("✅ Модуль успешно импортирован")
        
        # Принудительно загружаем
        print("🔄 Принудительная перезагрузка...")
        load_reality_tests()
        
        all_tests = get_all_user_tests()
        print(f"📊 Тестов в памяти: {len(all_tests)}")
        
        if all_tests:
            print("\n📋 Тесты в памяти:")
            for user_id, test_data in all_tests.items():
                print(f"  👤 Пользователь {user_id}:")
                print(f"     📈 Актив: {test_data.get('ticker', 'N/A')}")
                print(f"     📅 Дата проверки: {test_data.get('target_date', 'N/A')}")
                print()
        else:
            print("❌ Нет тестов в памяти")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {str(e)}")
    except Exception as e:
        print(f"❌ Ошибка модуля: {str(e)}")
    
    # Проверяем рабочую директорию
    print(f"\n📁 Рабочая директория: {os.getcwd()}")
    print(f"📋 Содержимое директории:")
    for item in os.listdir('.'):
        if item.startswith('reality'):
            print(f"  📄 {item}")
    
    print("=" * 50)
    print("🏁 Диагностика завершена")

if __name__ == "__main__":
    check_reality_tests_storage()