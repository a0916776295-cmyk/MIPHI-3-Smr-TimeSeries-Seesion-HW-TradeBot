#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка состояния пользователя для тестов реальности
"""

import os
import sys
import json

def check_user_states():
    """Проверяет текущие состояния пользователей"""
    print("🔍 Проверяем состояния пользователей...")
    
    try:
        if os.path.exists("user_states.json"):
            with open("user_states.json", "r", encoding="utf-8") as f:
                states = json.load(f)
            
            print(f"📊 Найдено пользователей: {len(states)}")
            
            for user_id, state in states.items():
                print(f"\n👤 Пользователь {user_id}:")
                print(f"   📈 ticker: {state.get('ticker', 'НЕТ')}")
                print(f"   💰 amount: {state.get('amount', 'НЕТ')}")
                print(f"   📅 forecast_days: {state.get('forecast_days', 'НЕТ')}")
                print(f"   🔧 mode: {state.get('mode', 'НЕТ')}")
                
                temp_forecast = state.get('temp_forecast')
                if temp_forecast:
                    print(f"   🧪 temp_forecast: ЕСТЬ")
                    print(f"      📈 ticker: {temp_forecast.get('ticker', 'НЕТ')}")
                    print(f"      🤖 model_name: {temp_forecast.get('model_name', 'НЕТ')}")
                    print(f"      💰 amount: {temp_forecast.get('amount', 'НЕТ')}")
                    print(f"      🔮 predictions: {type(temp_forecast.get('predictions', 'НЕТ'))}")
                    print(f"      📋 trading_recommendations: {len(temp_forecast.get('trading_recommendations', [])) if temp_forecast.get('trading_recommendations') else 'НЕТ'}")
                else:
                    print(f"   🧪 temp_forecast: НЕТ")
        else:
            print("❌ Файл user_states.json не найден")
            
    except Exception as e:
        print(f"❌ Ошибка чтения состояний: {e}")
        import traceback
        print(f"Детали: {traceback.format_exc()}")

def create_test_user_with_forecast():
    """Создает тестового пользователя с полным прогнозом"""
    print("\n🧪 Создаем тестового пользователя с прогнозом...")
    
    try:
        states = {}
        if os.path.exists("user_states.json"):
            with open("user_states.json", "r", encoding="utf-8") as f:
                states = json.load(f)
        
        # Добавляем тестового пользователя
        test_user_id = "999999"
        states[test_user_id] = {
            "ticker": "NVDA",
            "amount": 100,
            "forecast_days": 5,
            "mode": "selecting_test_date",
            "temp_forecast": {
                "ticker": "NVDA",
                "amount": 100,
                "model_name": "LSTM",
                "predictions": [190.0, 195.0, 200.0, 195.0, 185.0],
                "forecast_days": 5,
                "trading_recommendations": [
                    {
                        "action": "КУПИТЬ",
                        "date": "2026-01-10",
                        "price": 190.0,
                        "quantity": 0.52,
                        "profit": 0
                    },
                    {
                        "action": "ПРОДАТЬ", 
                        "date": "2026-01-12",
                        "price": 200.0,
                        "quantity": 0.52,
                        "profit": 5.2
                    }
                ],
                "expected_profit": 5.2,
                "profit_percent": 5.2,
                "created_at": "2026-01-10 21:41:00"
            }
        }
        
        # Сохраняем состояния
        with open("user_states.json", "w", encoding="utf-8") as f:
            json.dump(states, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Тестовый пользователь {test_user_id} создан с полным прогнозом")
        print("📱 Теперь можно тестировать создание теста реальности в Telegram боте")
        print("🔧 Используйте этот user_id в Telegram для тестирования")
        
    except Exception as e:
        print(f"❌ Ошибка создания тестового пользователя: {e}")
        import traceback
        print(f"Детали: {traceback.format_exc()}")

def main():
    print("🔍 ПРОВЕРКА СОСТОЯНИЙ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 50)
    
    # Проверяем текущие состояния
    check_user_states()
    
    # Создаем тестового пользователя
    create_test_user_with_forecast()
    
    print("\n" + "=" * 50)
    print("✅ Проверка завершена")

if __name__ == "__main__":
    main()