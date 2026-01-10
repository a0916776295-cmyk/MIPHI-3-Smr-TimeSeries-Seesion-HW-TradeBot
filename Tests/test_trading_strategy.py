# -*- coding: utf-8 -*-
"""
Тесты торговых стратегий и рекомендаций
"""

import unittest
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from trading_recommendations import (
        calculate_trading_strategy,
        generate_recommendations_text,
        save_recommendations_to_file
    )
except ImportError as e:
    print(f"❌ Ошибка импорта торгового модуля: {e}")

class TestTradingStrategy(unittest.TestCase):
    """Тесты торговых стратегий"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.test_predictions = np.array([100.0, 105.0, 110.0, 108.0, 115.0])
        self.test_dates = pd.date_range(
            start=datetime.now().date(),
            periods=5,
            freq='D'
        )
        self.test_amount = 1000
        self.test_current_price = 95.0
    
    def test_calculate_trading_strategy_basic(self):
        """Базовый тест расчета торговой стратегии"""
        try:
            recommendations, expected_profit, trades = calculate_trading_strategy(
                self.test_predictions,
                self.test_dates,
                self.test_amount,
                self.test_current_price
            )
            
            self.assertIsInstance(recommendations, list, "Рекомендации должны быть списком")
            self.assertIsInstance(expected_profit, (int, float), "Ожидаемая прибыль должна быть числом")
            self.assertIsInstance(trades, list, "Сделки должны быть списком")
            
            # Проверяем что есть хотя бы одна рекомендация
            self.assertGreater(len(recommendations), 0, "Должна быть хотя бы одна рекомендация")
            
        except Exception as e:
            self.fail(f"Ошибка в расчете торговой стратегии: {str(e)}")
    
    def test_generate_recommendations_text(self):
        """Тест генерации текста рекомендаций"""
        try:
            # Сначала получаем рекомендации
            recommendations, expected_profit, trades = calculate_trading_strategy(
                self.test_predictions,
                self.test_dates,
                self.test_amount,
                self.test_current_price
            )
            
            profit_percent = (expected_profit / self.test_amount) * 100
            
            # Генерируем текст
            text = generate_recommendations_text(
                recommendations,
                expected_profit,
                profit_percent,
                self.test_amount,
                "TEST"
            )
            
            self.assertIsInstance(text, str, "Текст рекомендаций должен быть строкой")
            self.assertGreater(len(text), 0, "Текст не должен быть пустым")
            self.assertIn("TEST", text, "В тексте должен быть указан тикер")
            
        except Exception as e:
            self.fail(f"Ошибка в генерации текста рекомендаций: {str(e)}")
    
    def test_trading_strategy_profit_calculation(self):
        """Тест расчета прибыли в торговой стратегии"""
        try:
            # Используем предсказуемые данные для проверки логики
            rising_predictions = np.array([100.0, 110.0, 120.0, 130.0, 140.0])
            
            recommendations, expected_profit, trades = calculate_trading_strategy(
                rising_predictions,
                self.test_dates,
                self.test_amount,
                100.0  # Текущая цена равна первому прогнозу
            )
            
            # При растущем тренде должна быть положительная прибыль
            self.assertGreaterEqual(expected_profit, 0, "При растущем тренде прибыль должна быть положительной или нулевой")
            
        except Exception as e:
            self.fail(f"Ошибка в расчете прибыли: {str(e)}")
    
    def test_trading_strategy_with_volatile_data(self):
        """Тест торговой стратегии с волатильными данными"""
        try:
            # Волатильные данные
            volatile_predictions = np.array([100.0, 90.0, 110.0, 85.0, 115.0])
            
            recommendations, expected_profit, trades = calculate_trading_strategy(
                volatile_predictions,
                self.test_dates,
                self.test_amount,
                100.0
            )
            
            # Должны получить рекомендации даже для волатильных данных
            self.assertIsInstance(recommendations, list, "Рекомендации должны быть списком")
            self.assertIsInstance(expected_profit, (int, float), "Прибыль должна быть числом")
            
        except Exception as e:
            self.fail(f"Ошибка обработки волатильных данных: {str(e)}")

class TestTradingRecommendationsValidation(unittest.TestCase):
    """Тесты валидации торговых рекомендаций"""
    
    def test_empty_predictions(self):
        """Тест обработки пустых прогнозов"""
        try:
            empty_predictions = np.array([])
            empty_dates = pd.date_range(start=datetime.now().date(), periods=0, freq='D')
            
            recommendations, expected_profit, trades = calculate_trading_strategy(
                empty_predictions,
                empty_dates,
                1000,
                100.0
            )
            
            # Должны получить пустые результаты без ошибок
            self.assertEqual(len(recommendations), 0, "Для пустых данных не должно быть рекомендаций")
            self.assertEqual(expected_profit, 0, "Прибыль должна быть нулевой")
            
        except Exception as e:
            self.fail(f"Ошибка обработки пустых данных: {str(e)}")
    
    def test_single_prediction(self):
        """Тест обработки одного прогноза"""
        try:
            single_prediction = np.array([105.0])
            single_date = pd.date_range(start=datetime.now().date(), periods=1, freq='D')
            
            recommendations, expected_profit, trades = calculate_trading_strategy(
                single_prediction,
                single_date,
                1000,
                100.0
            )
            
            # Должны получить результат без ошибок
            self.assertIsInstance(recommendations, list, "Результат должен быть списком")
            self.assertIsInstance(expected_profit, (int, float), "Прибыль должна быть числом")
            
        except Exception as e:
            self.fail(f"Ошибка обработки одного прогноза: {str(e)}")

if __name__ == '__main__':
    print("🧪 Запуск тестов торговых стратегий...")
    print("=" * 50)
    
    # Запускаем тесты
    unittest.main(verbosity=2, exit=False)
    
    print("=" * 50)
    print("✅ Тестирование торговых стратегий завершено!")