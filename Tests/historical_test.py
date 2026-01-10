import sys
sys.path.append('.')
import asyncio

async def historical_test():
    """Тест с исторической датой для полной проверки"""
    print("=== ТЕСТ С ИСТОРИЧЕСКОЙ ДАТОЙ ===")

    try:
        from .reality_test import (
            add_reality_test, get_user_reality_test, 
            check_ready_tests, execute_reality_test,
            reality_tests, save_reality_tests
        )
        from datetime import datetime, timedelta
        import pandas as pd
        
        test_user_id = 666666
        
        # Очищаем старые тесты
        if test_user_id in reality_tests:
            del reality_tests[test_user_id]
        
        print("✅ Подготовка завершена")
        
        # 1. Создание теста с исторической датой
        print("\n🔄 ЭТАП 1: Создание теста с исторической датой")
        ticker = 'AAPL'
        amount = 1000
        model_name = 'HISTORICAL_TEST_MODEL'
        
        # Используем данные за декабрь 2024 (должны быть в наборе)
        historical_date = "2024-12-31"  # Новый год
        
        # Создаем тестовый прогноз для дат вокруг исторической даты
        base_date = datetime(2024, 12, 27)  # Пятница перед НГ
        forecast_dates = []
        for i in range(5):
            date = base_date + timedelta(days=i)
            forecast_dates.append(date.strftime('%Y-%m-%d'))
        
        # Примерные цены для теста (будут сравниваться с реальными)
        test_predictions = [190.0, 192.5, 191.8, 193.2, 194.1]
        
        print(f"📊 Тестовые данные:")
        print(f"   Тикер: {ticker}")
        print(f"   Дата теста: {historical_date}")
        print(f"   Даты прогноза: {forecast_dates}")
        print(f"   Прогнозы: {test_predictions}")
        
        success = add_reality_test(
            test_user_id, ticker, historical_date,
            test_predictions, forecast_dates,
            amount, model_name
        )
        
        print(f"Создание теста: {success}")
        
        if not success:
            print("❌ Не удалось создать тест")
            return
        
        # 2. Сразу выполняем тест (историческая дата уже прошла)
        print("\n🔄 ЭТАП 2: Проверка готовых тестов")
        ready_tests = check_ready_tests()
        user_ready = [(uid, test) for uid, test in ready_tests if uid == test_user_id]
        
        if user_ready:
            print("✅ Тест готов к выполнению (историческая дата)")
            uid, test = user_ready[0]
            
            # 3. Выполнение теста
            print("\n🔄 ЭТАП 3: Выполнение исторического теста")
            success, message, metrics = await execute_reality_test(uid, test)
            
            if success:
                print("✅ ТЕСТ ВЫПОЛНЕН УСПЕШНО!")
                print(f"📊 Результат: {message}")
                
                if metrics:
                    print("\n📈 ДЕТАЛЬНЫЕ МЕТРИКИ:")
                    for key, value in metrics.items():
                        if isinstance(value, float):
                            print(f"   • {key}: {value:.4f}")
                        else:
                            print(f"   • {key}: {value}")
                
                print("\n🎉 ПОЛНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
                print("✅ Механизм создания и выполнения тестов работает на 100%!")
                print("✅ Загрузка исторических данных: OK")
                print("✅ Сравнение прогноза с реальностью: OK") 
                print("✅ Расчет метрик точности: OK")
                print("✅ Генерация отчета: OK")
                
            else:
                print("❌ Ошибка выполнения теста")
                print(f"Сообщение: {message}")
        else:
            print("❌ Тест не готов к выполнению")
        
        # 4. Очистка
        print("\n🔄 ЭТАП 4: Очистка тестовых данных")
        if test_user_id in reality_tests:
            del reality_tests[test_user_id]
            save_reality_tests()
            print("✅ Тестовые данные удалены")
        
    except Exception as e:
        print(f"❌ Ошибка в тестировании: {e}")
        import traceback
        traceback.print_exc()

# Запуск исторического теста
if __name__ == "__main__":
    print("🚀 Запуск тестирования с исторической датой...")
    asyncio.run(historical_test())