# -*- coding: utf-8 -*-
"""
Запуск всех тестов торгового бота
"""

import os
import sys
import unittest
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 ТОРГОВЫЙ БОТ - КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ")
    print("=" * 70)
    print(f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Определяем папку с тестами
    test_dir = os.path.dirname(__file__)
    
    # Загружаем все тесты
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Список тестовых модулей
    test_modules = [
        'test_main',
        'test_trading_strategy', 
        'test_reality'
    ]
    
    print("📋 Загружаемые тестовые модули:")
    
    for module_name in test_modules:
        try:
            # Пытаемся импортировать модуль
            module = __import__(module_name)
            
            # Загружаем тесты из модуля
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
            
            # Считаем количество тестов в модуле
            test_count = module_suite.countTestCases()
            print(f"  ✅ {module_name}: {test_count} тестов")
            
        except ImportError as e:
            print(f"  ❌ {module_name}: Ошибка импорта - {str(e)}")
        except Exception as e:
            print(f"  ⚠️ {module_name}: Ошибка загрузки - {str(e)}")
    
    total_tests = suite.countTestCases()
    print(f"\n📊 Всего тестов к выполнению: {total_tests}")
    print("=" * 70)
    
    if total_tests == 0:
        print("❌ Нет тестов для выполнения!")
        return False
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("🧪 ЗАПУСК ТЕСТОВ:")
    print("-" * 70)
    
    result = runner.run(suite)
    
    # Выводим итоги
    print("=" * 70)
    print("📈 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"🏃 Выполнено тестов: {result.testsRun}")
    print(f"✅ Успешных: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Неудачных: {len(result.failures)}")
    print(f"💥 Ошибок: {len(result.errors)}")
    print(f"⏭️ Пропущенных: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    # Детали неудач
    if result.failures:
        print("\n💔 ДЕТАЛИ НЕУДАЧ:")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n{i}. {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else traceback[:100]}...")
    
    # Детали ошибок
    if result.errors:
        print("\n💥 ДЕТАЛИ ОШИБОК:")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n{i}. {test}")
            error_lines = traceback.split('\n')
            error_msg = next((line for line in error_lines if 'Error:' in line), error_lines[-2] if len(error_lines) > 1 else "Unknown error")
            print(f"   {error_msg.strip()}")
    
    # Общий итог
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    
    print(f"\n🎯 УСПЕШНОСТЬ: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🏆 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        status = "ОТЛИЧНО"
    elif success_rate >= 80:
        print("✅ БОЛЬШИНСТВО ТЕСТОВ ПРОШЛИ УСПЕШНО!")
        status = "ХОРОШО"
    elif success_rate >= 60:
        print("⚠️ ЧАСТИЧНЫЙ УСПЕХ - ТРЕБУЕТСЯ ВНИМАНИЕ")
        status = "УДОВЛЕТВОРИТЕЛЬНО"
    else:
        print("❌ КРИТИЧЕСКИЕ ПРОБЛЕМЫ - ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ")
        status = "НЕУДОВЛЕТВОРИТЕЛЬНО"
    
    print("=" * 70)
    print(f"🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО: {status}")
    print(f"📅 Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return result.wasSuccessful()

def main():
    """Основная функция"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано пользователем")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка при тестировании: {str(e)}")
        sys.exit(3)

if __name__ == '__main__':
    main()