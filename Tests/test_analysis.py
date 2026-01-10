# -*- coding: utf-8 -*-
"""
Тест компонентов анализа
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

def test_analysis_components():
    """Тестируем компоненты анализа"""
    safe_print("🧪 Тестирование компонентов анализа...")
    
    try:
        # Тест 1: Импорт finance
        safe_print("\n1️⃣ Тестирование модуля finance...")
        from finance import get_finance_data
        safe_print("✅ finance импортирован")
        
        # Тест 2: Загрузка данных
        safe_print("\n2️⃣ Тестирование загрузки данных...")
        df = get_finance_data("AAPL")
        if df is not None:
            safe_print(f"✅ Данные загружены: {len(df)} записей")
        else:
            safe_print("❌ Данные не загружены")
        
        # Тест 3: Импорт model_comparison (может быть медленным)
        safe_print("\n3️⃣ Тестирование импорта model_comparison (может занять время)...")
        try:
            from Models.model_comparison import compare_all_models
            safe_print("✅ model_comparison импортирован")
        except Exception as e:
            safe_print(f"❌ Ошибка импорта model_comparison: {str(e)}")
        
        # Тест 4: Импорт trading_recommendations
        safe_print("\n4️⃣ Тестирование trading_recommendations...")
        try:
            from trading_recommendations import calculate_trading_strategy
            safe_print("✅ trading_recommendations импортирован")
        except Exception as e:
            safe_print(f"❌ Ошибка импорта trading_recommendations: {str(e)}")
        
        # Тест 5: Импорт graph
        safe_print("\n5️⃣ Тестирование graph...")
        try:
            from graph import generate_graph
            safe_print("✅ graph импортирован")
        except Exception as e:
            safe_print(f"❌ Ошибка импорта graph: {str(e)}")
        
        # Тест 6: Создание папки Tasks
        safe_print("\n6️⃣ Проверка папки Tasks...")
        if not os.path.exists("Tasks"):
            os.makedirs("Tasks")
            safe_print("✅ Папка Tasks создана")
        else:
            safe_print("✅ Папка Tasks уже существует")
        
        safe_print("\n🎉 Базовое тестирование завершено!")
        
    except Exception as e:
        safe_print(f"❌ Критическая ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

def quick_analysis_test():
    """Быстрый тест процесса анализа"""
    safe_print("\n🚀 Быстрый тест процесса анализа...")
    
    try:
        # Создаем минимальное состояние как в боте
        state = {
            "ticker": "AAPL",
            "amount": 1000,
            "forecast_days": 5  # Короткий прогноз для быстроты
        }
        
        safe_print(f"📊 Тестовые параметры:")
        safe_print(f"   Тикер: {state['ticker']}")
        safe_print(f"   Сумма: ${state['amount']}")
        safe_print(f"   Дни: {state['forecast_days']}")
        
        # Загружаем данные
        from finance import get_finance_data
        df = get_finance_data(state["ticker"])
        
        if df is None:
            safe_print("❌ Не удалось загрузить данные")
            return
        
        safe_print(f"✅ Данные загружены: {len(df)} записей")
        
        # Проверяем достаточность данных
        if len(df) < 100:
            safe_print(f"❌ Недостаточно данных: {len(df)} < 100")
            return
        
        safe_print("✅ Данных достаточно для анализа")
        safe_print("✅ Базовая проверка анализа пройдена!")
        
    except Exception as e:
        safe_print(f"❌ Ошибка в быстром тесте: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    safe_print("🔍 Диагностика компонентов анализа")
    safe_print("=" * 50)
    
    test_analysis_components()
    quick_analysis_test()
    
    safe_print("\n" + "=" * 50)
    safe_print("🏁 Диагностика завершена!")
    
    input("\nНажмите Enter для выхода...")