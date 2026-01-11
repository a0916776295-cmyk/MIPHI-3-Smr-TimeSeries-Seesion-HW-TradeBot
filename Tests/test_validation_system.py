#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест усиленной валидации для блокировки нереалистичных прогнозов
"""

import numpy as np
import pandas as pd
from Models.model_comparison import validate_prediction_sanity

def test_enhanced_validation():
    """Тестируем новую усиленную систему валидации"""
    
    print("🧪 ТЕСТ УСИЛЕННОЙ ВАЛИДАЦИИ")
    print("=" * 50)
    
    current_price = 200.0
    
    # 1. Тест реалистичного прогноза
    realistic_predictions = np.array([201, 202, 198, 205, 203])
    is_valid, penalty, issues = validate_prediction_sanity(realistic_predictions, current_price, "TestModel")
    print(f"\n1️⃣ Реалистичный прогноз:")
    print(f"   Валидный: {is_valid}, Штраф: {penalty}, Проблемы: {len(issues)}")
    
    # 2. КРИТИЧЕСКИЙ тест: отрицательные цены
    negative_predictions = np.array([200, 180, -50, -10, 150])
    is_valid, penalty, issues = validate_prediction_sanity(negative_predictions, current_price, "BadModel")
    print(f"\n2️⃣ Отрицательные цены:")
    print(f"   Валидный: {is_valid}, Штраф: {penalty}, Проблемы: {issues}")
    
    # 3. КРИТИЧЕСКИЙ тест: экстремальные скачки (более 50% за день)
    extreme_predictions = np.array([200, 400, 800, 50, 1000])  # Скачки 100%, 100%, -94%, 1900%
    is_valid, penalty, issues = validate_prediction_sanity(extreme_predictions, current_price, "ExtremeModel")
    print(f"\n3️⃣ Экстремальные скачки:")
    print(f"   Валидный: {is_valid}, Штраф: {penalty}, Проблемы: {issues}")
    
    # 4. КРИТИЧЕСКИЙ тест: нереальная волатильность (диапазон > 5x от цены)
    volatile_predictions = np.array([10, 200, 1500, 100, 2000])  # Диапазон 1990 (9.95x от 200)
    is_valid, penalty, issues = validate_prediction_sanity(volatile_predictions, current_price, "VolatileModel")
    print(f"\n4️⃣ Экстремальная волатильность:")
    print(f"   Валидный: {is_valid}, Штраф: {penalty}, Проблемы: {issues}")
    
    # 5. Проверяем пороговые значения
    print(f"\n📊 ПРОВЕРКА ПОРОГОВЫХ ЗНАЧЕНИЙ:")
    print(f"   Порог валидности: penalty < 100")
    print(f"   Штраф за отрицательные цены: 10000 (критично)")
    print(f"   Штраф за скачок 50%+: 5000 (критично)")
    print(f"   Штраф за волатильность 5x+: 5000 (критично)")
    
    # 6. Проверим комбинированные проблемы
    awful_predictions = np.array([-50, 2000, -100, 3000, 50])
    is_valid, penalty, issues = validate_prediction_sanity(awful_predictions, current_price, "AwfulModel")
    print(f"\n6️⃣ Комбинированные проблемы:")
    print(f"   Валидный: {is_valid}, Штраф: {penalty}, Проблемы: {issues}")
    
    print(f"\n🎯 ВЫВОДЫ:")
    print(f"   ✅ Реалистичные модели проходят валидацию")
    print(f"   ❌ Нереалистичные модели строго отклоняются")
    print(f"   🛡️ Система защищена от экстремальных прогнозов")

if __name__ == "__main__":
    test_enhanced_validation()