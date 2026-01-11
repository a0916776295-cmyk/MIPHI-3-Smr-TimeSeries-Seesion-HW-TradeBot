# -*- coding: utf-8 -*-
"""
Быстрый тест исправлений
"""

import sys
sys.path.append('.')

from Models.model_comparison import validate_prediction_sanity
import numpy as np

def quick_test():
    print("🧪 Быстрый тест исправлений")
    
    # Тест валидации
    normal_pred = np.array([100, 102, 98, 105, 103])
    is_valid, penalty, issues = validate_prediction_sanity(normal_pred, 100, 'Test')
    
    if is_valid and penalty == 0:
        print("✅ Система валидации работает")
    else:
        print(f"❌ Проблема с валидацией: valid={is_valid}, penalty={penalty}")
    
    # Тест с плохими данными
    bad_pred = np.array([100, -10, -100])
    is_valid, penalty, issues = validate_prediction_sanity(bad_pred, 100, 'BadTest')
    
    if not is_valid and penalty > 500:
        print("✅ Система штрафов работает")
    else:
        print(f"❌ Проблема со штрафами: valid={is_valid}, penalty={penalty}")
    
    print("🎉 Все проверки пройдены!")

if __name__ == "__main__":
    quick_test()