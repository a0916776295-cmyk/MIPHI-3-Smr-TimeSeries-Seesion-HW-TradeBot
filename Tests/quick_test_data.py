# -*- coding: utf-8 -*-
"""
Быстрая диагностика загрузки данных для конкретного тикера
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

def test_specific_ticker(ticker):
    """Тестирует загрузку данных для конкретного тикера"""
    safe_print(f"🔍 Тестирование тикера: {ticker}")
    safe_print("=" * 40)
    
    try:
        from finance import get_finance_data
        
        # Тестируем загрузку
        safe_print("⏳ Загружаю данные...")
        df = get_finance_data(ticker)
        
        if df is None:
            safe_print(f"❌ Данные для {ticker} не загружены")
            safe_print("💡 Возможные причины:")
            safe_print("   • Неверный тикер")
            safe_print("   • Проблемы с интернетом")
            safe_print("   • Временная недоступность Yahoo Finance")
        else:
            safe_print(f"✅ Данные успешно загружены!")
            safe_print(f"📊 Записей: {len(df)}")
            safe_print(f"📅 Период: {df.index[0].date()} - {df.index[-1].date()}")
            safe_print(f"📈 Колонки: {list(df.columns)}")
            safe_print(f"💰 Последняя цена закрытия: ${df['Close'].iloc[-1]:.2f}")
            safe_print(f"📈 Последняя максимальная: ${df['High'].iloc[-1]:.2f}")
            safe_print(f"📉 Последняя минимальная: ${df['Low'].iloc[-1]:.2f}")
            safe_print(f"📊 Объем торгов: {df['Volume'].iloc[-1]:,.0f}")
            
            # Проверяем качество данных
            if len(df) < 100:
                safe_print("⚠️ ВНИМАНИЕ: Мало данных для анализа (< 100 дней)")
            else:
                safe_print(f"✅ Достаточно данных для анализа ({len(df)} дней)")
    
    except Exception as e:
        safe_print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    safe_print("🚀 Диагностика загрузки данных")
    safe_print("")
    
    # Можно указать конкретный тикер для тестирования
    test_ticker = input("Введите тикер для тестирования (или нажмите Enter для AAPL): ").strip().upper()
    if not test_ticker:
        test_ticker = "AAPL"
    
    test_specific_ticker(test_ticker)
    
    safe_print("")
    safe_print("🔄 Хотите протестировать еще один тикер? (y/n)")
    if input().lower() == 'y':
        another_ticker = input("Введите тикер: ").strip().upper()
        if another_ticker:
            safe_print("")
            test_specific_ticker(another_ticker)

if __name__ == "__main__":
    main()