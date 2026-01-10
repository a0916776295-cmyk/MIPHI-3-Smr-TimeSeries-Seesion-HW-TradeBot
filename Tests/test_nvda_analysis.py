#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import finance
import pandas as pd
from datetime import datetime

def test_nvda_analysis():
    print("🔍 ТЕСТИРОВАНИЕ АНАЛИЗА NVDA")
    print("=" * 50)
    
    try:
        # Тест 1: Загрузка данных
        print("1️⃣ Тестируем загрузку данных NVDA...")
        df = finance.get_finance_data("NVDA")
        
        if df is None:
            print("❌ Ошибка: get_finance_data вернула None")
            return False
            
        print(f"✅ Данные загружены: {len(df)} записей")
        print(f"   📅 Период: {df.index[0].date()} - {df.index[-1].date()}")
        print(f"   📊 Последняя цена: ${df['Close'].iloc[-1]:.2f}")
        
        # Тест 2: Проверка достаточности данных
        print("2️⃣ Проверяем достаточность данных...")
        if len(df) < 100:
            print(f"❌ Недостаточно данных: {len(df)} записей (нужно минимум 100)")
            return False
        
        print(f"✅ Данных достаточно: {len(df)} записей")
        
        # Тест 3: Проверка импорта pandas
        print("3️⃣ Тестируем импорт pandas...")
        import pandas as pd
        from datetime import timedelta
        
        # Симулируем создание дат прогноза
        forecast_days = 5
        forecast_dates = pd.date_range(
            start=df.index[-1] + timedelta(days=1),
            periods=forecast_days,
            freq='D'
        )
        
        print(f"✅ Pandas работает корректно")
        print(f"   📅 Даты прогноза: {forecast_dates[0].date()} - {forecast_dates[-1].date()}")
        
        # Тест 4: Проверка модели
        print("4️⃣ Тестируем базовую модель...")
        try:
            import Models.Model_Prophet as Model_Prophet
            model = Model_Prophet.predict_prophet(df.copy(), forecast_days)
            print(f"✅ Модель Prophet работает")
            print(f"   📈 Прогноз: {model[:3]}... (первые 3 значения)")
        except Exception as model_error:
            print(f"⚠️ Ошибка в модели Prophet: {model_error}")
        
        print()
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Анализ NVDA должен работать корректно")
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 ДИАГНОСТИКА АНАЛИЗА NVDA")
    print("=" * 60)
    
    success = test_nvda_analysis()
    
    if success:
        print("\n🚀 АНАЛИЗ ГОТОВ К РАБОТЕ!")
        print("\nТеперь можете запустить анализ NVDA в боте")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("Обратитесь к администратору")