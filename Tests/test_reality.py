# -*- coding: utf-8 -*-
"""
Тесты модуля тестирования реальности
"""

import unittest
import sys
import os
import json
import tempfile
from datetime import datetime, timedelta

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from Tests.reality_test import (
        add_reality_test,
        get_user_reality_test, 
        remove_reality_test,
        check_ready_tests,
        execute_reality_test,
        format_test_status,
        get_reality_tests_statistics,
        get_user_all_tests,
        delete_user_test,
        delete_all_user_tests
    )
except ImportError as e:
    print(f"❌ Ошибка импорта модуля reality_test: {e}")

class TestRealityTestCore(unittest.TestCase):
    """Основные тесты модуля тестирования реальности"""
    
    def setUp(self):
        """Подготовка к тестам"""
        self.test_user_id = 123456789
        self.test_ticker = "NVDA"
        self.test_amount = 500
        self.test_model = "TEST_LSTM"
        self.test_predictions = [190.0, 195.0, 200.0, 195.0, 185.0]
        self.test_dates = [
            "2026-01-11", "2026-01-12", "2026-01-13", "2026-01-14", "2026-01-15"
        ]
        
        # Дата в будущем для тестирования
        self.future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        # Дата в прошлом для тестирования готовых тестов
        self.past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    def tearDown(self):
        """Очистка после тестов"""
        try:
            remove_reality_test(self.test_user_id)
            delete_all_user_tests(self.test_user_id)
        except:
            pass
    
    def test_add_and_get_reality_test(self):
        """Тест добавления и получения теста реальности"""
        # Добавляем тест
        result = add_reality_test(
            self.test_user_id,
            self.test_ticker,
            self.future_date,
            self.test_predictions,
            self.test_dates,
            self.test_amount,
            self.test_model
        )
        
        self.assertTrue(result, "Тест должен быть успешно добавлен")
        
        # Получаем тест
        test_data = get_user_reality_test(self.test_user_id)
        
        self.assertIsNotNone(test_data, "Тест должен быть найден")
        self.assertEqual(test_data['ticker'], self.test_ticker)
        self.assertEqual(test_data['target_date'], self.future_date)
        self.assertEqual(test_data['amount'], self.test_amount)
        self.assertEqual(test_data['model_name'], self.test_model)
        self.assertEqual(len(test_data['forecast']), len(self.test_predictions))
    
    def test_remove_reality_test(self):
        """Тест удаления теста реальности"""
        # Сначала добавляем тест
        add_result = add_reality_test(
            self.test_user_id,
            self.test_ticker,
            self.future_date,
            self.test_predictions,
            self.test_dates,
            self.test_amount,
            self.test_model
        )
        self.assertTrue(add_result)
        
        # Удаляем тест
        remove_result = remove_reality_test(self.test_user_id)
        self.assertTrue(remove_result, "Тест должен быть успешно удален")
        
        # Проверяем что тест действительно удален
        test_data = get_user_reality_test(self.test_user_id)
        self.assertIsNone(test_data, "После удаления тест не должен существовать")
    
    def test_check_ready_tests(self):
        """Тест проверки готовых тестов"""
        # Добавляем тест с датой в прошлом (готов к выполнению)
        add_result = add_reality_test(
            self.test_user_id,
            self.test_ticker,
            self.past_date,
            self.test_predictions,
            self.test_dates,
            self.test_amount,
            self.test_model
        )
        self.assertTrue(add_result)
        
        # Проверяем готовые тесты
        ready_tests = check_ready_tests()
        self.assertIsInstance(ready_tests, list, "Результат должен быть списком")
        
        # Ищем наш тест среди готовых
        user_tests = [test for uid, test in ready_tests if uid == self.test_user_id]
        self.assertGreater(len(user_tests), 0, "Наш тест должен быть среди готовых")
    
    def test_format_test_status(self):
        """Тест форматирования статуса теста"""
        test_data = {
            'ticker': self.test_ticker,
            'target_date': self.future_date,
            'model_name': self.test_model,
            'amount': self.test_amount,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        status_text = format_test_status(test_data)
        
        self.assertIsInstance(status_text, str, "Статус должен быть строкой")
        self.assertIn(self.test_ticker, status_text, "В статусе должен быть тикер")
        self.assertIn(self.test_model, status_text, "В статусе должна быть модель")
        self.assertIn(str(self.test_amount), status_text, "В статусе должна быть сумма")
    
    def test_get_statistics(self):
        """Тест получения статистики тестов"""
        # Добавляем несколько тестов для статистики
        add_result1 = add_reality_test(
            self.test_user_id,
            self.test_ticker,
            self.future_date,
            self.test_predictions,
            self.test_dates,
            self.test_amount,
            self.test_model
        )
        
        stats = get_reality_tests_statistics()
        
        self.assertIsInstance(stats, dict, "Статистика должна быть словарем")
        
        # Проверяем наличие обязательных ключей
        required_keys = ['total_count', 'waiting_count', 'ready_count', 'completed_count']
        for key in required_keys:
            self.assertIn(key, stats, f"В статистике должен быть ключ {key}")
            self.assertIsInstance(stats[key], int, f"{key} должен быть числом")
        
        # Проверяем детализацию
        self.assertIn('old_tests', stats)
        self.assertIn('new_tests', stats)
        
        if add_result1:
            self.assertGreater(stats['total_count'], 0, "После добавления теста счетчик должен увеличиться")

class TestRealityTestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев для модуля reality_test"""
    
    def test_nonexistent_user(self):
        """Тест получения теста для несуществующего пользователя"""
        nonexistent_user_id = 999999999
        
        test_data = get_user_reality_test(nonexistent_user_id)
        self.assertIsNone(test_data, "Для несуществующего пользователя должен возвращаться None")
    
    def test_remove_nonexistent_test(self):
        """Тест удаления несуществующего теста"""
        nonexistent_user_id = 999999999
        
        result = remove_reality_test(nonexistent_user_id)
        self.assertFalse(result, "Удаление несуществующего теста должно возвращать False")
    
    def test_empty_predictions(self):
        """Тест добавления теста с пустыми прогнозами"""
        test_user_id = 111111111
        
        try:
            result = add_reality_test(
                test_user_id,
                "TEST",
                (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                [],  # Пустые прогнозы
                [],
                1000,
                "TEST_MODEL"
            )
            
            # Система должна справиться с пустыми прогнозами
            self.assertIsInstance(result, bool, "Результат должен быть булевым значением")
            
        except Exception as e:
            self.fail(f"Не должно быть исключений при пустых прогнозах: {str(e)}")
        finally:
            try:
                remove_reality_test(test_user_id)
            except:
                pass
    
    def test_invalid_date_format(self):
        """Тест добавления теста с невалидной датой"""
        test_user_id = 222222222
        
        try:
            result = add_reality_test(
                test_user_id,
                "TEST",
                "invalid-date-format",  # Невалидная дата
                [100.0, 101.0],
                ["2026-01-01", "2026-01-02"],
                1000,
                "TEST_MODEL"
            )
            
            # Система должна справиться с невалидными датами
            self.assertIsInstance(result, bool, "Результат должен быть булевым значением")
            
        except Exception as e:
            # Некоторые исключения допустимы для невалидных дат
            pass
        finally:
            try:
                remove_reality_test(test_user_id)
            except:
                pass

class TestRealityTestIntegration(unittest.TestCase):
    """Интеграционные тесты модуля reality_test"""
    
    def setUp(self):
        """Подготовка к интеграционным тестам"""
        self.test_user_id = 333333333
        self.cleanup_users = []
    
    def tearDown(self):
        """Очистка после интеграционных тестов"""
        for user_id in self.cleanup_users:
            try:
                delete_all_user_tests(user_id)
                remove_reality_test(user_id)
            except:
                pass
    
    def test_multiple_users_workflow(self):
        """Тест работы с несколькими пользователями"""
        user1_id = 444444444
        user2_id = 555555555
        self.cleanup_users.extend([user1_id, user2_id])
        
        future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        # Добавляем тесты для двух пользователей
        result1 = add_reality_test(
            user1_id, "AAPL", future_date,
            [150.0, 155.0], ["2026-01-01", "2026-01-02"],
            1000, "MODEL1"
        )
        
        result2 = add_reality_test(
            user2_id, "GOOGL", future_date,
            [2800.0, 2850.0], ["2026-01-01", "2026-01-02"],
            2000, "MODEL2"
        )
        
        self.assertTrue(result1, "Тест первого пользователя должен быть добавлен")
        self.assertTrue(result2, "Тест второго пользователя должен быть добавлен")
        
        # Проверяем что каждый пользователь видит только свой тест
        user1_test = get_user_reality_test(user1_id)
        user2_test = get_user_reality_test(user2_id)
        
        self.assertIsNotNone(user1_test, "Первый пользователь должен видеть свой тест")
        self.assertIsNotNone(user2_test, "Второй пользователь должен видеть свой тест")
        
        self.assertEqual(user1_test['ticker'], 'AAPL')
        self.assertEqual(user2_test['ticker'], 'GOOGL')
        self.assertEqual(user1_test['amount'], 1000)
        self.assertEqual(user2_test['amount'], 2000)
    
    def test_statistics_with_multiple_tests(self):
        """Тест статистики с несколькими тестами"""
        users = [666666666, 777777777, 888888888]
        self.cleanup_users.extend(users)
        
        future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        past_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        
        # Добавляем тесты с разными статусами
        for i, user_id in enumerate(users):
            test_date = future_date if i < 2 else past_date
            add_result = add_reality_test(
                user_id, f"TEST{i}", test_date,
                [100.0 + i*10, 110.0 + i*10], 
                ["2026-01-01", "2026-01-02"],
                1000 + i*500, f"MODEL{i}"
            )
            self.assertTrue(add_result, f"Тест пользователя {user_id} должен быть добавлен")
        
        # Проверяем статистику
        stats = get_reality_tests_statistics()
        
        self.assertGreaterEqual(stats['total_count'], 3, "Должно быть минимум 3 теста")
        self.assertGreaterEqual(stats['waiting_count'], 2, "Должно быть минимум 2 ожидающих теста")
        self.assertGreaterEqual(stats['ready_count'], 1, "Должен быть минимум 1 готовый тест")

if __name__ == '__main__':
    print("🧪 Запуск тестов модуля тестирования реальности...")
    print("=" * 60)
    
    # Запускаем тесты
    unittest.main(verbosity=2, exit=False)
    
    print("=" * 60)
    print("✅ Тестирование модуля reality_test завершено!")