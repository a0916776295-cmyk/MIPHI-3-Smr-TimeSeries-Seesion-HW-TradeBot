#!/usr/bin/env python3
"""
Тестирование исправленных функций генерации текста рекомендаций
"""
from trading_recommendations import generate_recommendations_text, generate_brief_recommendations_text

# Тестовые данные с числовыми ценами (как должно быть)
test_recommendations_numeric = [
    {
        'date': '09.01.2026',
        'day': 0,
        'action': '🟢 ПОКУПАТЬ',
        'price': 100.0,  # Числовое значение
        'shares': 2.0,
        'expected_profit': 10.0,
        'reason': 'Прогнозируется рост до $105.00 (+5.0%)'
    },
    {
        'date': '11.01.2026',
        'day': 2,
        'action': '🔴 ПРОДАВАТЬ',
        'price': 105.0,  # Числовое значение
        'shares': 2.0,
        'expected_profit': 10.0,
        'reason': 'Фиксация прибыли (+5.0%)'
    }
]

# Тестовые данные со строковыми ценами (проблемный случай)
test_recommendations_string = [
    {
        'date': '09.01.2026',
        'day': 0,
        'action': '🟢 ПОКУПАТЬ',
        'price': "100.0",  # Строковое значение
        'shares': 2.0,
        'expected_profit': 10.0,
        'reason': 'Прогнозируется рост до $105.00 (+5.0%)'
    },
    {
        'date': '11.01.2026',
        'day': 2,
        'action': '🔴 ПРОДАВАТЬ',
        'price': "105.0",  # Строковое значение
        'shares': 2.0,
        'expected_profit': 10.0,
        'reason': 'Фиксация прибыли (+5.0%)'
    }
]

print("=" * 70)
print("ТЕСТИРОВАНИЕ ИСПРАВЛЕННЫХ ФУНКЦИЙ ГЕНЕРАЦИИ ТЕКСТА")
print("=" * 70)

# Тест 1: Числовые цены
print("\n1. ТЕСТИРОВАНИЕ С ЧИСЛОВЫМИ ЦЕНАМИ:")
print("-" * 50)
try:
    full_text = generate_recommendations_text(
        test_recommendations_numeric, 
        expected_profit=20.0, 
        profit_percent=10.0, 
        initial_investment=200, 
        ticker="TEST"
    )
    print("✅ Полный формат с числовыми ценами - УСПЕШНО")
    
    brief_text = generate_brief_recommendations_text(test_recommendations_numeric, "TEST")
    print("✅ Краткий формат с числовыми ценами - УСПЕШНО")
    
except Exception as e:
    print(f"❌ ОШИБКА с числовыми ценами: {e}")

# Тест 2: Строковые цены (должно работать после исправления)
print("\n2. ТЕСТИРОВАНИЕ СО СТРОКОВЫМИ ЦЕНАМИ:")
print("-" * 50)
try:
    full_text = generate_recommendations_text(
        test_recommendations_string, 
        expected_profit=20.0, 
        profit_percent=10.0, 
        initial_investment=200, 
        ticker="TEST"
    )
    print("✅ Полный формат со строковыми ценами - УСПЕШНО")
    print("✅ Исправление float() работает корректно!")
    
    brief_text = generate_brief_recommendations_text(test_recommendations_string, "TEST")
    print("✅ Краткий формат со строковыми ценами - УСПЕШНО")
    
except Exception as e:
    print(f"❌ ОШИБКА со строковыми ценами: {e}")

print("\n" + "=" * 70)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 70)