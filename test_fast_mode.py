#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест быстрого режима обучения моделей
"""

import sys
sys.path.append('.')

import yfinance as yf
from Models.model_comparison import compare_all_models

def test_fast_mode():
    print("⚡ ТЕСТИРОВАНИЕ БЫСТРОГО РЕЖИМА")
    print("=" * 50)
    
    # Загружаем данные
    ticker = yf.Ticker('NVDA')
    df = ticker.history(period='1y', interval='1d')
    print(f"📊 Данных: {len(df)} записей")
    
    task_folder = 'fast_mode_test'
    import os
    os.makedirs(task_folder, exist_ok=True)
    
    # Тест быстрого режима
    print("\n🚀 Запуск БЫСТРОГО режима...")
    import time
    start_time = time.time()
    
    try:
        best_model, second_best_model, comparison_data = compare_all_models(df, 5, task_folder, fast_mode=True)
        fast_time = time.time() - start_time
        
        print(f"\n✅ БЫСТРЫЙ режим завершен за {fast_time:.1f}с")
        print(f"🏆 Лучшая модель: {best_model['model_name']}")
        print(f"📊 RMSE: {best_model['rmse']:.2f}, MAPE: {best_model['mape']:.2f}%")
        
        if 'sanity_check' in best_model:
            print(f"🔍 Реалистичность: {best_model['sanity_check']['is_valid']}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fast_mode()