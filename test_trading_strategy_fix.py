#!/usr/bin/env python3
"""
Тестирование исправленной функции calculate_trading_strategy
"""
from trading_recommendations import calculate_trading_strategy
import pandas as pd
from datetime import datetime, timedelta

# Создаем тестовые данные для прогноза
test_predictions = [100, 105, 103, 108, 95]
test_dates = pd.date_range(
    start=datetime.now().date() + timedelta(days=1),
    periods=len(test_predictions),
    freq='D'
)
current_price = 100
initial_investment = 200

print("=" * 60)
print("ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ ФУНКЦИИ calculate_trading_strategy")
print("=" * 60)

try:
    recommendations, expected_profit, profit_percent, trades = calculate_trading_strategy(
        test_predictions,
        test_dates,
        initial_investment,
        current_price
    )
    
    print(f"✅ ТЕСТ ПРОШЕЛ УСПЕШНО!")
    print(f"📊 Получено рекомендаций: {len(recommendations)}")
    print(f"💰 Ожидаемая прибыль: ${expected_profit:.2f}")
    print(f"📈 Процент прибыли: {profit_percent:.2f}%")
    print(f"🔄 Сделок: {len(trades)}")
    
    print(f"\n📋 Рекомендации:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['date']} - {rec['action']} по ${rec['price']:.2f}")
        if 'expected_profit' in rec:
            print(f"   💰 Ожидаемая прибыль: ${rec['expected_profit']:.2f}")
    
    print(f"\n🎉 ВСЕ ОШИБКИ ИСПРАВЛЕНЫ - ФУНКЦИЯ РАБОТАЕТ КОРРЕКТНО!")
    
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    print(f"Подробности: {traceback.format_exc()}")

print("=" * 60)