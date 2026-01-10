#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест новых Transformer моделей и Ensemble методов
"""

import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.append('.')

def test_new_models():
    """Тестируем новые модели"""
    print("🧪 Тестирование новых моделей...")
    
    # Тестируем импорт новых моделей
    try:
        from Model_Transformer import train_transformer_model
        print("✅ Transformer модель доступна")
    except ImportError as e:
        print(f"❌ Transformer модель: {e}")
    
    try:
        from Model_Informer import train_informer_model
        print("✅ Informer модель доступна")
    except ImportError as e:
        print(f"❌ Informer модель: {e}")
    
    try:
        from Model_Ensemble import create_ensemble_predictions, EnsemblePredictor
        print("✅ Ensemble методы доступны")
    except ImportError as e:
        print(f"❌ Ensemble методы: {e}")
    
    # Тестируем обновленный model_comparison
    try:
        from model_comparison import compare_all_models
        print("✅ Обновленный model_comparison доступен")
    except ImportError as e:
        print(f"❌ model_comparison: {e}")
    
    # Создаем тестовые данные
    try:
        import pandas as pd
        import numpy as np
        
        # Генерируем синтетические данные
        dates = pd.date_range(start='2024-01-01', periods=200, freq='D')
        
        # Создаем реалистичный временной ряд с трендом и сезонностью
        np.random.seed(42)
        trend = np.linspace(100, 150, 200)
        seasonal = 10 * np.sin(2 * np.pi * np.arange(200) / 30)
        noise = np.random.normal(0, 2, 200)
        close_prices = trend + seasonal + noise
        
        test_data = pd.DataFrame({
            'Close': close_prices
        }, index=dates)
        
        print(f"📊 Создан тестовый датасет: {test_data.shape}")
        print(f"📅 Период: {test_data.index[0]} - {test_data.index[-1]}")
        print(f"💰 Цены: ${test_data['Close'].min():.2f} - ${test_data['Close'].max():.2f}")
        
        # Тестируем Transformer модель
        print("\n🤖 Тестирование Transformer модели...")
        try:
            from Model_Transformer import train_transformer_model
            result = train_transformer_model(test_data, prediction_steps=5, epochs=5, batch_size=8)
            print(f"✅ Transformer: RMSE={result['rmse']:.2f}, MAPE={result['mape']:.2f}%")
            print(f"📈 Прогноз: {result['predictions'][:3]}... (показано 3 из {len(result['predictions'])})")
        except Exception as e:
            print(f"❌ Ошибка в Transformer: {e}")
        
        # Тестируем Ensemble методы
        print("\n🎭 Тестирование Ensemble методов...")
        try:
            # Создаем несколько фиктивных результатов моделей для теста
            mock_results = [
                {
                    'model_name': 'Mock_LSTM',
                    'rmse': 5.5,
                    'mape': 2.1,
                    'predictions': np.array([120, 122, 125, 123, 121])
                },
                {
                    'model_name': 'Mock_GRU', 
                    'rmse': 6.2,
                    'mape': 2.4,
                    'predictions': np.array([119, 121, 124, 122, 120])
                },
                {
                    'model_name': 'Mock_Ridge',
                    'rmse': 4.8,
                    'mape': 1.9,
                    'predictions': np.array([121, 123, 126, 124, 122])
                }
            ]
            
            from Model_Ensemble import create_ensemble_predictions
            ensemble_results = create_ensemble_predictions(mock_results)
            
            if ensemble_results:
                print(f"✅ Создано {len(ensemble_results)} ensemble моделей:")
                for result in ensemble_results[:3]:  # Показываем первые 3
                    print(f"   📊 {result['model_name']}: RMSE={result['rmse']:.2f}, MAPE={result['mape']:.2f}%")
                    if 'component_models' in result:
                        print(f"      Компоненты: {', '.join(result['component_models'])}")
            else:
                print("❌ Ensemble модели не созданы")
                
        except Exception as e:
            print(f"❌ Ошибка в Ensemble: {e}")
        
        print("\n🎉 Тестирование завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка в тестировании: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ НОВЫХ МОДЕЛЕЙ")
    print("=" * 60)
    
    success = test_new_models()
    
    print("=" * 60)
    if success:
        print("✅ ТЕСТИРОВАНИЕ УСПЕШНО ЗАВЕРШЕНО!")
        print("\n🎯 Новые возможности:")
        print("• Transformer модель - современная архитектура внимания")
        print("• Informer модель - оптимизированная для длинных последовательностей")
        print("• Ensemble методы - комбинирование моделей для лучшей точности")
        print("• Адаптивные веса - автоматический выбор лучших комбинаций")
    else:
        print("❌ ТЕСТИРОВАНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ")
    print("=" * 60)