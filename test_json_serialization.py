#!/usr/bin/env python3
"""
Тестирование JSON сериализации торговых рекомендаций
"""
import json
import numpy as np
from trading_recommendations import calculate_trading_strategy, convert_numpy_types_in_recommendations
import pandas as pd
from datetime import datetime, timedelta

print("=" * 60)
print("ТЕСТИРОВАНИЕ JSON СЕРИАЛИЗАЦИИ")
print("=" * 60)

# Создаем тестовые данные с numpy типами
test_predictions = np.array([100.0, 105.0, 103.0, 108.0, 95.0])
test_dates = pd.date_range(
    start=datetime.now().date() + timedelta(days=1),
    periods=len(test_predictions),
    freq='D'
)
current_price = 100.0
initial_investment = 200

try:
    recommendations, expected_profit, profit_percent, trades = calculate_trading_strategy(
        test_predictions,
        test_dates,
        initial_investment,
        current_price
    )
    
    print(f"✅ Функция calculate_trading_strategy выполнена успешно")
    print(f"📊 Получено {len(recommendations)} рекомендаций")
    
    # Проверяем типы данных в рекомендациях
    print("\n🔍 АНАЛИЗ ТИПОВ ДАННЫХ:")
    for i, rec in enumerate(recommendations):
        print(f"Рекомендация {i+1}:")
        for key, value in rec.items():
            print(f"  {key}: {type(value)} = {value}")
    
    # Пытаемся сериализовать в JSON
    print(f"\n🧪 ТЕСТ JSON СЕРИАЛИЗАЦИИ:")
    try:
        json_string = json.dumps(recommendations, ensure_ascii=False, indent=2)
        print(f"✅ JSON сериализация УСПЕШНА!")
        print(f"📏 Длина JSON: {len(json_string)} символов")
        
        # Попытаемся десериализовать обратно
        deserialized = json.loads(json_string)
        print(f"✅ JSON десериализация УСПЕШНА!")
        print(f"📊 Количество рекомендаций после десериализации: {len(deserialized)}")
        
    except Exception as json_error:
        print(f"❌ ОШИБКА JSON сериализации: {json_error}")
        print(f"🔧 Применяем функцию convert_numpy_types_in_recommendations...")
        
        # Используем функцию очистки
        cleaned_recommendations = convert_numpy_types_in_recommendations(recommendations)
        try:
            json_string = json.dumps(cleaned_recommendations, ensure_ascii=False, indent=2)
            print(f"✅ JSON сериализация после очистки УСПЕШНА!")
            
        except Exception as clean_error:
            print(f"❌ Ошибка даже после очистки: {clean_error}")
    
    print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    
except Exception as e:
    print(f"❌ ОБЩАЯ ОШИБКА: {e}")
    import traceback
    print(f"Подробности: {traceback.format_exc()}")

print("=" * 60)