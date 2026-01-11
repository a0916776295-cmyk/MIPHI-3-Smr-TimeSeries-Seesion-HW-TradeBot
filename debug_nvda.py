# -*- coding: utf-8 -*-
"""
Тест проблемы с NVDA
"""

import yfinance as yf
import os
import sys
sys.path.append('.')

from Models.model_comparison import compare_all_models

def test_nvda_issue():
    print('📈 Тестирование проблемы с NVDA...')
    
    # Загрузка данных NVDA
    print('⬇️ Загружаю данные NVDA...')
    ticker = yf.Ticker('NVDA')
    df = ticker.history(period='2y', interval='1d')

    if df.empty:
        print('❌ Не удалось загрузить данные')
        return
    else:
        print(f'✅ Загружено {len(df)} записей')
        print(f'📅 Диапазон дат: {df.index[0]} - {df.index[-1]}')
        print(f'💰 Последняя цена: ${df["Close"].iloc[-1]:.2f}')
    
    task_folder = 'temp_test'
    os.makedirs(task_folder, exist_ok=True)
    
    print('\n🧠 Запуск сравнения моделей...')
    try:
        best_model, second_best_model, comparison_data = compare_all_models(df, 5, task_folder)
        print('✅ Сравнение завершено успешно')
        print(f'🏆 Лучшая модель: {best_model["model_name"]}')
        print(f'📊 RMSE: {best_model["rmse"]:.2f}, MAPE: {best_model["mape"]:.2f}%')
        
        if 'sanity_check' in best_model:
            print(f'✔️ Проверка реалистичности: {best_model["sanity_check"]["is_valid"]}')
        
    except Exception as e:
        print(f'❌ ОШИБКА: {str(e)}')
        import traceback
        print('\n📋 Детальная трассировка:')
        traceback.print_exc()

if __name__ == "__main__":
    test_nvda_issue()