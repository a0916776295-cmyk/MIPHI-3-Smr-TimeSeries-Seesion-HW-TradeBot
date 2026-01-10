#!/usr/bin/env python3
"""
Тестирование нового формата торговых рекомендаций
"""
from trading_recommendations import generate_brief_recommendations_text, generate_recommendations_text

# Тестовые данные рекомендаций
test_recommendations = [
    {
        'date': '09.01.2026',
        'day': 0,
        'action': '🟢 ПОКУПАТЬ',
        'price': 246.81,
        'shares': 0.8103,
        'expected_profit': 35.78,
        'reason': 'Прогнозируется рост до $290.97 (+17.9%)'
    },
    {
        'date': '14.01.2026',
        'day': 5,
        'action': '🔴 ФИНАЛЬНАЯ ПРОДАЖА',
        'price': 290.97,
        'shares': 0.8103,
        'expected_profit': 35.78,
        'reason': 'Закрытие позиции (+17.9%)'
    }
]

print("=" * 60)
print("ТЕСТИРОВАНИЕ НОВОГО ФОРМАТА ТОРГОВЫХ РЕКОМЕНДАЦИЙ")
print("=" * 60)

print("\n1. КРАТКИЙ ФОРМАТ (дата-действие-цена-прибыль):")
print("-" * 50)
brief_format = generate_brief_recommendations_text(test_recommendations, "AMZN")
print(brief_format)

print("\n2. ПОЛНЫЙ ФОРМАТ:")
print("-" * 50)
full_format = generate_recommendations_text(
    test_recommendations, 
    expected_profit=35.78, 
    profit_percent=17.89, 
    initial_investment=200, 
    ticker="AMZN"
)
print(full_format)

print("\n3. ТЕСТИРОВАНИЕ ПУСТОГО СПИСКА:")
print("-" * 50)
empty_brief = generate_brief_recommendations_text([], "TEST")
print(empty_brief)

print("\n=" * 60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 60)