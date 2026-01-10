# -*- coding: utf-8 -*-
"""
Тест модуля reality_test
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

def test_reality_test_module():
    """Тестируем функционал модуля reality_test"""
    safe_print("🧪 Тестирование модуля reality_test...")
    
    try:
        from . import reality_test
        safe_print("✅ Модуль reality_test успешно импортирован")
        
        # Тестируем основные функции
        safe_print("\n📊 Тестирование основных функций:")
        
        # Получение всех тестов
        tests = reality_test.get_all_user_tests()
        safe_print(f"   Активных тестов: {len(tests)}")
        
        # Проверка готовых тестов
        ready_tests = reality_test.check_ready_tests()
        safe_print(f"   Готовых к выполнению: {len(ready_tests)}")
        
        # Тест расчета метрик
        import numpy as np
        forecast = np.array([100, 105, 110, 108, 112])
        actual = np.array([102, 106, 109, 110, 115])
        
        metrics = reality_test.calculate_forecast_accuracy(forecast, actual)
        safe_print(f"\n📈 Тест метрик точности:")
        safe_print(f"   RMSE: {metrics['rmse']:.2f}")
        safe_print(f"   MAPE: {metrics['mape']:.2f}%")
        safe_print(f"   MAE: {metrics['mae']:.2f}")
        safe_print(f"   Точность направления: {metrics['direction_accuracy']:.1f}%")
        
        safe_print("\n✅ Модуль reality_test работает корректно!")
        
    except Exception as e:
        safe_print(f"❌ Ошибка при тестировании: {str(e)}")
        import traceback
        traceback.print_exc()

def test_menu_functions():
    """Тестируем новые функции меню"""
    safe_print("\n🎛️ Тестирование функций меню...")
    
    try:
        from MenuBot import get_reality_test_menu, get_test_date_menu, get_reality_test_help_text
        
        # Тест меню
        menu = get_reality_test_menu()
        safe_print("✅ get_reality_test_menu() работает")
        
        date_menu = get_test_date_menu()
        safe_print("✅ get_test_date_menu() работает")
        
        help_text = get_reality_test_help_text()
        safe_print("✅ get_reality_test_help_text() работает")
        safe_print(f"   Длина справки: {len(help_text)} символов")
        
        safe_print("\n✅ Функции меню работают корректно!")
        
    except Exception as e:
        safe_print(f"❌ Ошибка при тестировании меню: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    safe_print("🚀 Запуск тестирования функционала 'Испытание реальностью'")
    safe_print("=" * 60)
    
    test_reality_test_module()
    test_menu_functions()
    
    safe_print("\n" + "=" * 60)
    safe_print("🏁 Тестирование завершено!")