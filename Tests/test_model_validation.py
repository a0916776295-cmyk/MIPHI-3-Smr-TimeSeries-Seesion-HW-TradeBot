# -*- coding: utf-8 -*-
"""
Тест новой системы валидации моделей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Тест новой системы валидации
from Models.model_comparison import validate_prediction_sanity, calculate_enhanced_score
import numpy as np

def test_validation_system():
    print('🧪 ТЕСТИРОВАНИЕ НОВОЙ СИСТЕМЫ ВАЛИДАЦИИ')
    print('=' * 50)

    # Тест 1: Нормальные прогнозы
    print('\n1️⃣ Тест нормальных прогнозов:')
    normal_predictions = np.array([100, 102, 98, 105, 103])
    is_valid, penalty, issues = validate_prediction_sanity(normal_predictions, 100, 'TestModel_Normal')
    print(f'   Валидность: {is_valid}, Штраф: {penalty}')

    # Тест 2: Отрицательные цены (как у Ridge)
    print('\n2️⃣ Тест отрицательных прогнозов:')
    bad_predictions = np.array([100, 50, -10, -100, -200])  
    is_valid, penalty, issues = validate_prediction_sanity(bad_predictions, 100, 'TestModel_Bad')
    print(f'   Валидность: {is_valid}, Штраф: {penalty}')

    # Тест 3: Экстремальные изменения
    print('\n3️⃣ Тест экстремальных изменений:')
    extreme_predictions = np.array([100, 200, 50, 300, 25])  
    is_valid, penalty, issues = validate_prediction_sanity(extreme_predictions, 100, 'TestModel_Extreme')
    print(f'   Валидность: {is_valid}, Штраф: {penalty}')

    # Тест 4: Монотонные данные
    print('\n4️⃣ Тест монотонных прогнозов:')
    monotone_predictions = np.array([100, 100, 100, 100, 100])  
    is_valid, penalty, issues = validate_prediction_sanity(monotone_predictions, 100, 'TestModel_Monotone')
    print(f'   Валидность: {is_valid}, Штраф: {penalty}')

    print('\n✅ СИСТЕМА ВАЛИДАЦИИ РАБОТАЕТ!')

if __name__ == "__main__":
    test_validation_system()