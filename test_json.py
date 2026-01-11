import json

# Проверяем JSON файл reality_tests.json
try:
    with open('reality_tests.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'✅ JSON файл корректен')
    print(f'📊 Загружено тестов: {len(data)}')
    
    for user_id, test_data in data.items():
        print(f'   👤 Пользователь {user_id}: {test_data["ticker"]} на {test_data["target_date"]}')
        
except json.JSONDecodeError as e:
    print(f'❌ Ошибка JSON: {e}')
except Exception as e:
    print(f'❌ Другая ошибка: {e}')