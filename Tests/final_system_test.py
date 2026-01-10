# -*- coding: utf-8 -*-
"""
Финальный тест системы загрузки данных
"""

import sys
import os

# Настройка кодировки для Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def safe_print(text):
    """Безопасный вывод текста с поддержкой кириллицы"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print("Output encoding error")

def final_system_test():
    """Финальный тест всей системы"""
    safe_print("🚀 ФИНАЛЬНЫЙ ТЕСТ СИСТЕМЫ")
    safe_print("=" * 50)
    
    try:
        # 1. Тестируем импорты
        safe_print("\n1️⃣ Тестирование импортов...")
        from finance import get_finance_data
        from MenuBot import POPULAR_TICKERS, get_main_menu
        from reality_test import add_reality_test, check_ready_tests
        safe_print("✅ Все модули импортированы успешно")
        
        # 2. Тестируем загрузку данных для нескольких популярных тикеров
        safe_print("\n2️⃣ Тестирование загрузки данных...")
        test_tickers = ['AAPL', 'GOOGL', 'MSFT']
        working_count = 0
        
        for ticker in test_tickers:
            safe_print(f"   📊 Тестирую {ticker}...")
            df = get_finance_data(ticker)
            if df is not None and len(df) >= 100:
                safe_print(f"   ✅ {ticker}: {len(df)} записей, последняя цена: ${df['Close'].iloc[-1]:.2f}")
                working_count += 1
            else:
                safe_print(f"   ❌ {ticker}: Проблема с данными")
        
        if working_count == len(test_tickers):
            safe_print("✅ Загрузка данных работает отлично!")
        elif working_count > 0:
            safe_print(f"⚠️ Частичные проблемы: {working_count}/{len(test_tickers)} тикеров работают")
        else:
            safe_print("❌ Серьезные проблемы с загрузкой данных")
        
        # 3. Тестируем меню
        safe_print("\n3️⃣ Тестирование интерфейса...")
        menu = get_main_menu()
        safe_print(f"✅ Главное меню создано: {len(menu.keyboard)} строк кнопок")
        
        # 4. Тестируем систему реальности
        safe_print("\n4️⃣ Тестирование системы 'Испытание реальностью'...")
        ready_tests = check_ready_tests()
        safe_print(f"✅ Система тестирования работает: {len(ready_tests)} готовых тестов")
        
        # 5. Общий итог
        safe_print("\n" + "=" * 50)
        safe_print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ")
        safe_print("=" * 50)
        
        if working_count == len(test_tickers):
            safe_print("🟢 ВСЁ ОТЛИЧНО!")
            safe_print("   Система полностью работоспособна")
            safe_print("   Все тикеры загружаются корректно")
            safe_print("   Бот готов к использованию")
        elif working_count > 0:
            safe_print("🟡 ЧАСТИЧНЫЕ ПРОБЛЕМЫ")
            safe_print(f"   {working_count} из {len(test_tickers)} тикеров работают")
            safe_print("   Система в основном работоспособна")
            safe_print("   Некоторые тикеры могут быть временно недоступны")
        else:
            safe_print("🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ")
            safe_print("   Не удается загрузить данные ни для одного тикера")
            safe_print("   Проверьте интернет соединение или попробуйте позже")
        
        safe_print(f"\n💡 Рекомендации:")
        safe_print("   • Используйте /debug в боте для диагностики")
        safe_print("   • При проблемах попробуйте другие тикеры")
        safe_print("   • Обновите библиотеку yfinance: pip install --upgrade yfinance")
        
    except Exception as e:
        safe_print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        safe_print("\n🆘 Обратитесь к разработчику для исправления проблемы")

if __name__ == "__main__":
    final_system_test()
    safe_print("\n🏁 Тестирование завершено!")
    input("\nНажмите Enter для выхода...")