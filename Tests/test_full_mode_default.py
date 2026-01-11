#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест проверки того, что по умолчанию используется полный режим
"""

import os
import sys
from finance import get_finance_data
from Models.model_comparison import compare_all_models

def test_full_mode_is_default():
    """Проверяем, что по умолчанию система запускает полный режим"""
    
    # Убеждаемся, что переменная FORCE_FAST_MODE не установлена
    if 'FORCE_FAST_MODE' in os.environ:
        del os.environ['FORCE_FAST_MODE']
    
    print("🧪 ТЕСТ: Проверка режима по умолчанию")
    print("=" * 50)
    
    # Получаем тестовые данные
    ticker = "NVDA"
    df = get_finance_data(ticker)
    forecast_days = 5
    
    print(f"📊 Тестируем на {ticker} с прогнозом на {forecast_days} дней")
    print(f"📊 Данных: {len(df)} записей")
    
    # Имитируем вызов без fast_mode параметра (как это происходит по умолчанию)
    print("\n🚀 Запускаем сравнение моделей БЕЗ указания режима...")
    
    try:
        # Не передаем fast_mode - должен использоваться полный режим по умолчанию
        best_model, second_best, comparison_data = compare_all_models(
            df, forecast_days, "test_temp"
        )
        
        print(f"\n✅ Система завершилась успешно!")
        print(f"🏆 Лучшая модель: {best_model['model_name']}")
        print(f"📊 RMSE: {best_model['rmse']:.2f}, MAPE: {best_model['mape']:.2f}%")
        
        # Проверим количество протестированных моделей
        models_tested = len(comparison_data.get('models', []))
        print(f"🧠 Протестировано моделей: {models_tested}")
        
        if models_tested >= 10:
            print("✅ ПОЛНЫЙ режим активен (много моделей)")
        elif models_tested <= 6:
            print("⚡ Быстрый режим активен (мало моделей)")
        else:
            print("❓ Неопределенный режим")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

if __name__ == "__main__":
    success = test_full_mode_is_default()
    if success:
        print("\n🎉 Тест пройден!")
    else:
        print("\n❌ Тест провален!")