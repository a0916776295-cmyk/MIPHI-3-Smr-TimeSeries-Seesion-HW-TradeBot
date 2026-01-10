import sys
sys.path.append('.')

print("=== ТЕСТ МЕХАНИЗМА РЕАЛЬНОСТИ ===")

try:
    from .reality_test import add_reality_test, get_user_reality_test
    print("✅ Модуль reality_test импортирован")
    
    from datetime import datetime, timedelta
    import pandas as pd
    
    # Тестовые данные
    test_user_id = 999999
    ticker = 'AAPL'
    amount = 1000
    model_name = 'TEST_MODEL'
    test_predictions = [150.0, 151.5, 149.8, 152.2, 150.9]
    
    # Даты
    forecast_dates = pd.date_range(
        start=datetime.now().date(),
        periods=5,
        freq='D'
    ).strftime('%Y-%m-%d').tolist()
    
    test_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📊 Тестовые данные: {ticker}, ${amount}, {test_date}")
    
    # Создаем тест
    success = add_reality_test(
        test_user_id, ticker, test_date, 
        test_predictions, forecast_dates, 
        amount, model_name
    )
    
    print(f"📋 Результат создания теста: {success}")
    
    if success:
        # Проверяем сохранение
        saved_test = get_user_reality_test(test_user_id)
        if saved_test:
            print("✅ Тест найден в базе данных!")
            print(f"   Тикер: {saved_test['ticker']}")
            print(f"   Дата: {saved_test['target_date']}")
            print(f"   Модель: {saved_test['model_name']}")
            print(f"   Прогнозов: {len(saved_test['forecast'])}")
        else:
            print("❌ Тест не найден в базе")
    
    print("🧪 Базовое тестирование завершено!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()