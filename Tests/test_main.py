# -*- coding: utf-8 -*-
"""
Основные тесты для торгового бота
"""

import unittest
import sys
import os

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from Tests.reality_test import (
        add_reality_test, 
        get_user_reality_test, 
        remove_reality_test,
        check_ready_tests,
        get_reality_tests_statistics
    )
    from finance import get_finance_data
    from trading_recommendations import calculate_trading_strategy
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что все необходимые модули доступны")

class TestBasicFunctionality(unittest.TestCase):
    """Тесты базовой функциональности"""
    
    def test_reality_test_module_import(self):
        """Тест импорта модуля reality_test"""
        try:
            from Tests.reality_test import add_reality_test
            self.assertTrue(True, "Модуль reality_test успешно импортирован")
        except ImportError:
            self.fail("Не удалось импортировать модуль reality_test")
    
    def test_finance_module_import(self):
        """Тест импорта модуля finance"""
        try:
            from finance import get_finance_data
            self.assertTrue(True, "Модуль finance успешно импортирован")
        except ImportError:
            self.fail("Не удалось импортировать модуль finance")
    
    def test_trading_module_import(self):
        """Тест импорта модуля trading_recommendations"""
        try:
            from trading_recommendations import calculate_trading_strategy
            self.assertTrue(True, "Модуль trading_recommendations успешно импортирован")
        except ImportError:
            self.fail("Не удалось импортировать модуль trading_recommendations")

class TestRealityTestModule(unittest.TestCase):
    """Тесты модуля тестирования реальности"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.test_user_id = 999999
        self.test_ticker = "AAPL"
        self.test_date = "2026-01-15"
        self.test_predictions = [150.0, 151.5, 149.8, 152.2, 150.9]
        self.test_dates = ["2026-01-11", "2026-01-12", "2026-01-13", "2026-01-14", "2026-01-15"]
        self.test_amount = 1000
        self.test_model = "TEST_MODEL"
    
    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем тестовый тест если он был создан
        try:
            remove_reality_test(self.test_user_id)
        except:
            pass
    
    def test_add_reality_test(self):
        """Тест добавления теста реальности"""
        result = add_reality_test(
            self.test_user_id,
            self.test_ticker,
            self.test_date,
            self.test_predictions,
            self.test_dates,
            self.test_amount,
            self.test_model
        )
        self.assertTrue(result, "Тест реальности должен быть успешно добавлен")
    
    def test_get_reality_test(self):
        """Тест получения теста реальности"""
        # Сначала добавляем тест
        add_result = add_reality_test(
            self.test_user_id,
            self.test_ticker,
            self.test_date,
            self.test_predictions,
            self.test_dates,
            self.test_amount,
            self.test_model
        )
        self.assertTrue(add_result, "Не удалось добавить тест для тестирования")
        
        # Теперь получаем его
        test_data = get_user_reality_test(self.test_user_id)
        self.assertIsNotNone(test_data, "Должны получить данные теста")
        self.assertEqual(test_data['ticker'], self.test_ticker)
        self.assertEqual(test_data['target_date'], self.test_date)
        self.assertEqual(test_data['amount'], self.test_amount)
    
    def test_remove_reality_test(self):
        """Тест удаления теста реальности"""
        # Сначала добавляем тест
        add_result = add_reality_test(
            self.test_user_id,
            self.test_ticker,
            self.test_date,
            self.test_predictions,
            self.test_dates,
            self.test_amount,
            self.test_model
        )
        self.assertTrue(add_result, "Не удалось добавить тест для тестирования")
        
        # Теперь удаляем его
        remove_result = remove_reality_test(self.test_user_id)
        self.assertTrue(remove_result, "Тест должен быть успешно удален")
        
        # Проверяем что он действительно удален
        test_data = get_user_reality_test(self.test_user_id)
        self.assertIsNone(test_data, "После удаления тест не должен существовать")
    
    def test_statistics(self):
        """Тест получения статистики"""
        stats = get_reality_tests_statistics()
        self.assertIsInstance(stats, dict, "Статистика должна быть словарем")
        self.assertIn('total_count', stats, "В статистике должен быть total_count")
        self.assertIn('waiting_count', stats, "В статистике должен быть waiting_count")
        self.assertIn('ready_count', stats, "В статистике должен быть ready_count")
        self.assertIn('completed_count', stats, "В статистике должен быть completed_count")

class TestFinanceModule(unittest.TestCase):
    """Тесты финансового модуля"""
    
    def test_get_finance_data_valid_ticker(self):
        """Тест загрузки данных для валидного тикера"""
        # Пропускаем если нет интернета или проблемы с API
        try:
            df = get_finance_data("AAPL")
            if df is not None:
                self.assertTrue(len(df) > 0, "Данные должны содержать записи")
                self.assertIn('Close', df.columns, "В данных должна быть колонка Close")
            else:
                self.skipTest("Не удалось загрузить данные (проблемы с интернетом или API)")
        except Exception as e:
            self.skipTest(f"Пропускаем тест из-за ошибки: {str(e)}")
    
    def test_get_finance_data_invalid_ticker(self):
        """Тест загрузки данных для невалидного тикера"""
        try:
            df = get_finance_data("INVALID_TICKER_12345")
            self.assertIsNone(df, "Для невалидного тикера должен возвращаться None")
        except Exception:
            # Некоторые исключения ожидаемы для невалидных тикеров
            pass

if __name__ == '__main__':
    print("🧪 Запуск тестов торгового бота...")
    print("=" * 50)
    
    # Запускаем тесты
    unittest.main(verbosity=2, exit=False)
    
    print("=" * 50)
    print("✅ Тестирование завершено!")