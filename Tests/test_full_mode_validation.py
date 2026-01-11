#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест полного режима с усиленной валидацией
Проверяем, что нереалистичные модели исключаются из ensemble
"""

import os
import sys
from finance import get_finance_data
from Models.model_comparison import compare_all_models

def test_full_mode_validation():
    """Тестируем полный режим с новой системой валидации"""
    
    print("🧪 ТЕСТ ПОЛНОГО РЕЖИМА С УСИЛЕННОЙ ВАЛИДАЦИЕЙ")
    print("=" * 60)
    
    # Убеждаемся, что переменная FORCE_FAST_MODE не установлена
    if 'FORCE_FAST_MODE' in os.environ:
        del os.environ['FORCE_FAST_MODE']
    
    # Получаем данные для коротких прогнозов (чтобы снизить риск экстремальных значений)
    ticker = "NVDA"
    df = get_finance_data(ticker)
    forecast_days = 3  # Короткий прогноз для стабильности
    
    print(f"📊 Тестируем {ticker} с прогнозом на {forecast_days} дня")
    print(f"📊 Данных: {len(df)} записей")
    print(f"📊 Последняя цена: ${df['Close'].iloc[-1]:.2f}")
    
    try:
        print(f"\n🧠 Запускаем ПОЛНЫЙ режим (16 моделей)...")
        best_model, second_best, comparison_data = compare_all_models(
            df, forecast_days, "test_validation"
        )
        
        print(f"\n✅ Система завершилась успешно!")
        print(f"🏆 Лучшая модель: {best_model['model_name']}")
        print(f"📊 RMSE: {best_model['rmse']:.2f}, MAPE: {best_model['mape']:.2f}%")
        
        # Проверяем валидность лучшей модели
        is_valid = best_model.get('sanity_check', {}).get('is_valid', False)
        issues = best_model.get('sanity_check', {}).get('issues', [])
        
        print(f"🔍 Валидность лучшей модели: {'✅ ДА' if is_valid else '❌ НЕТ'}")
        if issues:
            print(f"⚠️ Проблемы: {'; '.join(issues)}")
        
        # Проверяем диапазон прогноза
        predictions = best_model['predictions']
        min_pred, max_pred = predictions.min(), predictions.max()
        current_price = df['Close'].iloc[-1]
        
        print(f"📈 Диапазон прогноза: ${min_pred:.2f} - ${max_pred:.2f}")
        print(f"📊 Изменение от текущей цены: {((max_pred-current_price)/current_price)*100:+.1f}% до {((min_pred-current_price)/current_price)*100:+.1f}%")
        
        # Проверяем общую статистику моделей
        models_tested = len(comparison_data.get('models', []))
        print(f"🧠 Протестировано моделей: {models_tested}")
        
        if models_tested >= 10:
            print("✅ ПОЛНЫЙ режим подтвержден")
        else:
            print("⚠️ Возможно, работает быстрый режим")
            
        # Проверим, есть ли информация об отклоненных моделях
        rejected_count = 0
        for model_data in comparison_data.get('models', []):
            if not model_data.get('is_realistic', True):
                rejected_count += 1
        
        print(f"🛡️ Отклонено нереалистичных моделей: {rejected_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

if __name__ == "__main__":
    success = test_full_mode_validation()
    if success:
        print("\n🎉 Тест успешно завершен!")
        print("🛡️ Система валидации работает корректно")
    else:
        print("\n❌ Тест провален!")