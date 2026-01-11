#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Детальная диагностика ошибок обучения моделей
"""

import os
import sys
import traceback
import yfinance as yf

# Добавляем корневую папку в путь
sys.path.append('.')

def diagnose_model_training():
    """Диагностика проблем с обучением моделей"""
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМ ОБУЧЕНИЯ МОДЕЛЕЙ")
    print("=" * 60)
    
    # Шаг 1: Проверка импорта
    print("\n1️⃣ Проверка импортов...")
    try:
        from Models.model_comparison import compare_all_models
        print("✅ Модуль model_comparison импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта model_comparison: {e}")
        traceback.print_exc()
        return
    
    # Шаг 2: Загрузка данных
    print("\n2️⃣ Проверка загрузки данных...")
    try:
        ticker = yf.Ticker('NVDA')
        df = ticker.history(period='1y', interval='1d')
        
        if df.empty:
            print("❌ Данные не загрузились")
            return
        
        print(f"✅ Загружено {len(df)} записей")
        print(f"📅 Диапазон: {df.index[0]} - {df.index[-1]}")
        print(f"💰 Последняя цена: ${df['Close'].iloc[-1]:.2f}")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        traceback.print_exc()
        return
    
    # Шаг 3: Создание папки для задач
    print("\n3️⃣ Подготовка рабочей папки...")
    task_folder = 'diagnostic_test'
    try:
        os.makedirs(task_folder, exist_ok=True)
        print(f"✅ Папка {task_folder} готова")
    except Exception as e:
        print(f"❌ Ошибка создания папки: {e}")
        return
    
    # Шаг 4: Тестирование простых моделей
    print("\n4️⃣ Тестирование отдельных моделей...")
    
    # Тест ARIMA
    try:
        from Models.Model_ARIMA import train_and_predict_arima
        result = train_and_predict_arima(df, 3)
        print(f"✅ ARIMA: RMSE={result['rmse']:.2f}")
    except Exception as e:
        print(f"❌ ARIMA: {str(e)[:80]}...")
    
    # Тест Ridge
    try:
        from Models.Model_Ridge import train_and_predict_ridge
        result = train_and_predict_ridge(df, 3)
        print(f"✅ Ridge: RMSE={result['rmse']:.2f}")
    except Exception as e:
        print(f"❌ Ridge: {str(e)[:80]}...")
    
    # Шаг 5: Полное сравнение с минимальным набором моделей
    print("\n5️⃣ Тестирование функции compare_all_models...")
    try:
        # Ограничиваем количество моделей для быстрой диагностики
        original_models = []
        
        best_model, second_best_model, comparison_data = compare_all_models(df, 3, task_folder)
        
        print("✅ compare_all_models выполнена успешно!")
        print(f"🏆 Лучшая модель: {best_model['model_name']}")
        print(f"📊 RMSE: {best_model['rmse']:.2f}")
        
        # Проверяем санитарные проверки
        if 'sanity_check' in best_model:
            is_valid = best_model['sanity_check']['is_valid']
            penalty = best_model['sanity_check']['penalty']
            print(f"🔍 Валидность: {is_valid}, Штраф: {penalty}")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в compare_all_models:")
        print(f"   Сообщение: {str(e)}")
        print("\n📋 Полная трассировка ошибки:")
        traceback.print_exc()
        
        # Дополнительная диагностика
        print("\n🔧 ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА:")
        print(f"   Размер данных: {df.shape}")
        print(f"   Колонки: {list(df.columns)}")
        print(f"   NaN значения: {df.isnull().sum().sum()}")
        print(f"   Индекс типа: {type(df.index)}")
        
    print("\n" + "=" * 60)
    print("🏁 ДИАГНОСТИКА ЗАВЕРШЕНА")

if __name__ == "__main__":
    diagnose_model_training()