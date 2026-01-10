import sys
sys.path.append('.')

print("=== ПОЛНЫЙ ТЕСТ МЕХАНИЗМА РЕАЛЬНОСТИ ===")

try:
    from .reality_test import (
        add_reality_test, get_user_reality_test, 
        check_ready_tests, execute_reality_test,
        reality_tests, save_reality_tests
    )
    from datetime import datetime, timedelta
    import pandas as pd
    
    test_user_id = 888888
    
    # Очищаем старые тесты
    if test_user_id in reality_tests:
        del reality_tests[test_user_id]
    
    print("✅ Импорты и очистка завершены")
    
    # 1. Создание теста
    print("\n🔄 ЭТАП 1: Создание теста")
    ticker = 'AAPL'
    amount = 500
    model_name = 'FULL_TEST_MODEL'
    test_predictions = [150.0, 151.5, 149.8, 152.2, 150.9]
    
    forecast_dates = pd.date_range(
        start=datetime.now().date(),
        periods=5,
        freq='D'
    ).strftime('%Y-%m-%d').tolist()
    
    test_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    success = add_reality_test(
        test_user_id, ticker, test_date,
        test_predictions, forecast_dates,
        amount, model_name
    )
    
    print(f"Создание теста: {success}")
    
    # 2. Проверка сохранения
    print("\n🔄 ЭТАП 2: Проверка сохранения")
    saved_test = get_user_reality_test(test_user_id)
    if saved_test:
        print("✅ Тест сохранен и найден")
    else:
        print("❌ Тест не найден")
        exit(1)
    
    # 3. Симуляция готовности (меняем дату на сегодня)
    print("\n🔄 ЭТАП 3: Симуляция готовности")
    reality_tests[test_user_id]["target_date"] = datetime.now().strftime('%Y-%m-%d')
    save_reality_tests()
    print(f"Дата теста изменена на: {datetime.now().strftime('%Y-%m-%d')}")
    
    # 4. Проверка готовых тестов
    print("\n🔄 ЭТАП 4: Проверка готовых тестов")
    ready_tests = check_ready_tests()
    user_ready = [(uid, test) for uid, test in ready_tests if uid == test_user_id]
    
    if user_ready:
        print("✅ Тест готов к выполнению")
        uid, test = user_ready[0]
        
        # 5. Выполнение теста
        print("\n🔄 ЭТАП 5: Выполнение теста")
        result = execute_reality_test(uid, test)
        
        if result and result.get('success'):
            print("✅ Тест выполнен успешно!")
            print(f"📊 Статус: {result['success']}")
            
            if 'report' in result:
                # Показываем первые 300 символов отчета
                report_preview = result['report'][:300]
                print(f"📋 Отчет (превью):\n{report_preview}...")
                
                # Сохраняем полный отчет в файл
                with open('test_reality_report.txt', 'w', encoding='utf-8') as f:
                    f.write(result['report'])
                print("📄 Полный отчет сохранен в test_reality_report.txt")
            
            print("\n🎉 ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ УСПЕШНО!")
            print("✅ Механизм создания и выполнения тестов реальности работает!")
            
        else:
            print("❌ Ошибка выполнения теста")
            if result:
                print(f"Детали: {result}")
    else:
        print("❌ Тест не готов к выполнению")
    
    # 6. Очистка
    print("\n🔄 ЭТАП 6: Очистка тестовых данных")
    if test_user_id in reality_tests:
        del reality_tests[test_user_id]
        save_reality_tests()
        print("✅ Тестовые данные удалены")
    
except Exception as e:
    print(f"❌ Ошибка в тестировании: {e}")
    import traceback
    traceback.print_exc()