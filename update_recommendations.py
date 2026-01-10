from trading_recommendations import generate_recommendations_text, save_recommendations_to_file
import os

# Тестовые рекомендации AMZN
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

# Создаем обновленный файл рекомендаций
task_folder = 'Tasks/AMZN-200-2026-01-09-2026-01-09'
save_recommendations_to_file(test_recommendations, 35.78, 17.89, 200, 'AMZN', task_folder)

print('✅ Файл рекомендаций обновлен с новым форматом!')