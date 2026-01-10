# -*- coding: utf-8 -*-
"""
Тест загрузки данных через yfinance
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

def test_yfinance_connection():
    """Тестируем соединение с Yahoo Finance"""
    safe_print("🔄 Тестирование загрузки данных...")
    
    try:
        import yfinance as yf
        safe_print("✅ Модуль yfinance импортирован успешно")
        
        # Тестируем загрузку данных для популярных тикеров
        test_tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
        
        for ticker in test_tickers:
            safe_print(f"\n📈 Тестируем тикер: {ticker}")
            try:
                # Загружаем данные за последние 5 дней для быстроты
                data = yf.download(ticker, period='5d', progress=False)
                
                if data is None or data.empty:
                    safe_print(f"❌ {ticker}: Данные не получены")
                else:
                    safe_print(f"✅ {ticker}: Получено {len(data)} записей")
                    safe_print(f"   Колонки: {list(data.columns)}")
                    safe_print(f"   Последняя цена: ${data['Close'].iloc[-1]:.2f}")
                    
            except Exception as e:
                safe_print(f"❌ {ticker}: Ошибка - {str(e)}")
    
    except ImportError as e:
        safe_print(f"❌ Ошибка импорта yfinance: {str(e)}")
        safe_print("💡 Попробуйте: pip install yfinance")
    except Exception as e:
        safe_print(f"❌ Общая ошибка: {str(e)}")

def test_finance_module():
    """Тестируем наш модуль finance.py"""
    safe_print("\n🧩 Тестирование модуля finance.py...")
    
    try:
        from finance import get_finance_data
        safe_print("✅ Модуль finance импортирован успешно")
        
        # Тестируем функцию get_finance_data
        test_tickers = ['AAPL', 'INVALID_TICKER', 'GOOGL']
        
        for ticker in test_tickers:
            safe_print(f"\n📊 Тестируем get_finance_data('{ticker}')...")
            
            try:
                df = get_finance_data(ticker)
                
                if df is None:
                    safe_print(f"❌ {ticker}: Функция вернула None")
                else:
                    safe_print(f"✅ {ticker}: Получен DataFrame")
                    safe_print(f"   Размер: {df.shape}")
                    safe_print(f"   Период: {df.index[0].date()} - {df.index[-1].date()}")
                    safe_print(f"   Колонки: {list(df.columns)}")
                    if 'Close' in df.columns:
                        safe_print(f"   Последняя цена: ${df['Close'].iloc[-1]:.2f}")
                    
            except Exception as e:
                safe_print(f"❌ {ticker}: Ошибка в get_finance_data - {str(e)}")
                import traceback
                traceback.print_exc()
    
    except ImportError as e:
        safe_print(f"❌ Ошибка импорта модуля finance: {str(e)}")
    except Exception as e:
        safe_print(f"❌ Общая ошибка в тестировании finance: {str(e)}")

def check_internet_connection():
    """Проверяем интернет соединение"""
    safe_print("\n🌐 Проверка интернет соединения...")
    
    try:
        import urllib.request
        
        # Проверяем доступность Yahoo Finance
        response = urllib.request.urlopen('https://finance.yahoo.com', timeout=10)
        if response.getcode() == 200:
            safe_print("✅ Доступ к finance.yahoo.com работает")
        else:
            safe_print(f"⚠️ finance.yahoo.com вернул код: {response.getcode()}")
            
    except Exception as e:
        safe_print(f"❌ Проблема с интернет соединением: {str(e)}")
        safe_print("💡 Проверьте подключение к интернету")

if __name__ == "__main__":
    safe_print("🚀 Диагностика проблем с загрузкой данных")
    safe_print("=" * 50)
    
    check_internet_connection()
    test_yfinance_connection()
    test_finance_module()
    
    safe_print("\n" + "=" * 50)
    safe_print("🏁 Диагностика завершена!")
    safe_print("\n💡 Если все тесты прошли успешно, проблема может быть в:")
    safe_print("   - Неправильном тикере акции")
    safe_print("   - Временных проблемах с Yahoo Finance")
    safe_print("   - Настройках прокси/файрвола")