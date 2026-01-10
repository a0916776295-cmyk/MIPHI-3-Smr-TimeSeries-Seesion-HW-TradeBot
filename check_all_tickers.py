# -*- coding: utf-8 -*-
"""
Проверка всех тикеров из MenuBot
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

def check_all_tickers():
    """Проверяет все тикеры из MenuBot"""
    safe_print("🔍 Проверка всех тикеров из MenuBot")
    safe_print("=" * 50)
    
    try:
        from MenuBot import POPULAR_TICKERS
        from finance import get_finance_data
        
        working_tickers = []
        failed_tickers = []
        
        total_tickers = len(POPULAR_TICKERS)
        current = 0
        
        for display_name, ticker in POPULAR_TICKERS.items():
            current += 1
            safe_print(f"\n[{current}/{total_tickers}] Тестирую {display_name} ({ticker})...")
            
            try:
                df = get_finance_data(ticker)
                if df is not None and len(df) >= 100:
                    working_tickers.append((display_name, ticker, len(df)))
                    safe_print(f"✅ {ticker}: {len(df)} записей")
                else:
                    failed_tickers.append((display_name, ticker, "Недостаточно данных" if df is not None else "Нет данных"))
                    safe_print(f"❌ {ticker}: {'Недостаточно данных' if df is not None else 'Нет данных'}")
                    
            except Exception as e:
                failed_tickers.append((display_name, ticker, str(e)))
                safe_print(f"❌ {ticker}: Ошибка - {str(e)[:50]}...")
        
        # Результаты
        safe_print("\n" + "=" * 50)
        safe_print("📊 ИТОГИ ПРОВЕРКИ")
        safe_print("=" * 50)
        
        safe_print(f"\n✅ РАБОТАЮЩИЕ ТИКЕРЫ ({len(working_tickers)}):")
        for display_name, ticker, count in working_tickers:
            safe_print(f"   {display_name}: {count} записей")
        
        if failed_tickers:
            safe_print(f"\n❌ ПРОБЛЕМНЫЕ ТИКЕРЫ ({len(failed_tickers)}):")
            for display_name, ticker, error in failed_tickers:
                safe_print(f"   {display_name}: {error}")
        
        safe_print(f"\n📈 Общая статистика:")
        safe_print(f"   Всего тикеров: {total_tickers}")
        safe_print(f"   Работают: {len(working_tickers)} ({len(working_tickers)/total_tickers*100:.1f}%)")
        safe_print(f"   Проблемы: {len(failed_tickers)} ({len(failed_tickers)/total_tickers*100:.1f}%)")
        
        if len(working_tickers) > len(failed_tickers):
            safe_print("\n🟢 Большинство тикеров работает нормально!")
        else:
            safe_print("\n🟡 Есть проблемы с загрузкой данных")
            
    except Exception as e:
        safe_print(f"❌ Ошибка при проверке: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_all_tickers()