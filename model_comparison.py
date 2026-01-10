import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Импорт всех моделей
from Model_ARIMA import train_and_predict_arima
from Model_SARIMA import train_and_predict_sarima
from Model_Prophet import train_and_predict_prophet
from Model_LSTM import train_and_predict_lstm
from Model_LSTM_optimized import train_and_predict_lstm as train_and_predict_lstm_opt
from Model_GRU import train_and_predict_gru
from Model_GRU_optimized import train_and_predict_gru as train_and_predict_gru_opt
from Model_TFT import train_and_predict_tft
from Model_Autoformer import train_and_predict_autoformer
from Model_FEDformer import train_and_predict_fedformer
from Model_Ridge import train_and_predict_ridge
from Model_RandomForest import train_and_predict_randomforest

# Новые Transformer-based модели
try:
    from Model_Transformer import train_transformer_model
    TRANSFORMER_AVAILABLE = True
    print("✅ Transformer модель успешно импортирована")
except ImportError as e:
    TRANSFORMER_AVAILABLE = False
    print(f"❌ Transformer модель не доступна: {e}")

try:
    from Model_Informer import train_informer_model
    INFORMER_AVAILABLE = True
    print("✅ Informer модель успешно импортирована")
except ImportError as e:
    INFORMER_AVAILABLE = False
    print(f"❌ Informer модель не доступна: {e}")

# Ensemble методы
try:
    from Model_Ensemble import create_ensemble_predictions
    ENSEMBLE_AVAILABLE = True
    print("✅ Ensemble методы успешно импортированы")
except ImportError as e:
    ENSEMBLE_AVAILABLE = False
    print(f"❌ Ensemble методы не доступны: {e}")

try:
    from Model_XGBoost import train_and_predict_xgboost
    XGBOOST_AVAILABLE = True
    print("✅ XGBoost успешно импортирован")
except ImportError as e:
    XGBOOST_AVAILABLE = False
    print(f"❌ XGBoost не установлен: {e}")

try:
    from Model_CatBoost import train_and_predict_catboost
    CATBOOST_AVAILABLE = True
    print("✅ CatBoost успешно импортирован")
except ImportError as e:
    CATBOOST_AVAILABLE = False
    print(f"❌ CatBoost не установлен: {e}")

def compare_all_models(df: pd.DataFrame, forecast_days: int, task_folder: str):
    """
    Сравнение всех моделей и выбор лучшей (включая новые Transformer и Ensemble модели)
    """
    models = [
        ('ARIMA', train_and_predict_arima),
        ('SARIMA', train_and_predict_sarima),
        ('Prophet', train_and_predict_prophet),
        ('LSTM', train_and_predict_lstm),
        ('LSTM_OPT', train_and_predict_lstm_opt),
        ('GRU', train_and_predict_gru),
        ('GRU_OPT', train_and_predict_gru_opt),
        ('TFT', train_and_predict_tft),
        ('Autoformer', train_and_predict_autoformer),
        ('FEDformer', train_and_predict_fedformer),
        ('Ridge', train_and_predict_ridge),
        ('RandomForest', train_and_predict_randomforest),
    ]
    
    # Добавляем новые Transformer-based модели
    if TRANSFORMER_AVAILABLE:
        models.append(('Transformer', lambda df, days: train_transformer_model(df, days)))
    
    if INFORMER_AVAILABLE:
        models.append(('Informer', lambda df, days: train_informer_model(df, days)))
    
    if XGBOOST_AVAILABLE:
        models.append(('XGBoost', train_and_predict_xgboost))
        print("✅ XGBoost добавлен в сравнение")
    else:
        print("⚠️ XGBoost пропущен")
    
    if CATBOOST_AVAILABLE:
        models.append(('CatBoost', train_and_predict_catboost))
        print("✅ CatBoost добавлен в сравнение")
    else:
        print("⚠️ CatBoost пропущен")
    
    print(f"Запуск сравнения {len(models)} моделей...")
    print(f"Модели: {[m[0] for m in models]}")
    
    results = []
    
    for model_name, model_func in models:
        try:
            print(f"Обучение модели {model_name}...")
            result = model_func(df, forecast_days)
            results.append(result)
            print(f"{model_name}: RMSE={result['rmse']:.2f}, MAPE={result['mape']:.2f}%")
        except Exception as e:
            print(f"Ошибка в модели {model_name}: {str(e)}")
    
    # Сортировка моделей по RMSE
    sorted_results = sorted(results, key=lambda x: x['rmse'])
    
    # Создаем ensemble модели (если доступно и есть достаточно моделей)
    ensemble_results = []
    if ENSEMBLE_AVAILABLE and len(results) >= 2:
        print(f"\n🤖 Создание Ensemble моделей...")
        try:
            ensemble_results = create_ensemble_predictions(results)
            if ensemble_results:
                # Добавляем ensemble результаты к общим результатам
                all_results = results + ensemble_results
                sorted_results = sorted(all_results, key=lambda x: x['rmse'])
                print(f"✅ Добавлено {len(ensemble_results)} ensemble моделей")
        except Exception as e:
            print(f"❌ Ошибка при создании ensemble: {str(e)}")
            ensemble_results = []
    
    # Лучшая и вторая лучшая модели (могут быть ensemble)
    best_model = sorted_results[0]
    second_best_model = sorted_results[1] if len(sorted_results) > 1 else None
    
    # Проверяем, является ли лучшая модель ensemble
    is_ensemble_winner = hasattr(best_model, 'get') and 'ensemble_type' in best_model
    
    if is_ensemble_winner:
        print(f"\n🎉 Победитель - Ensemble модель!")
        print(f"   Тип: {best_model.get('ensemble_type', 'unknown')}")
        if 'component_models' in best_model:
            print(f"   Компоненты: {', '.join(best_model['component_models'])}")
    
    # Сохранение результатов сравнения
    comparison_data = {
        'timestamp': datetime.now().isoformat(),
        'forecast_days': forecast_days,
        'total_models': len(results),
        'ensemble_models': len(ensemble_results),
        'models': [
            {
                'name': r['model_name'],
                'rmse': float(r['rmse']),
                'mape': float(r['mape']),
                'is_ensemble': 'ensemble_type' in r if isinstance(r, dict) else False
            }
            for r in sorted_results
        ],
        'best_model': {
            'name': best_model['model_name'],
            'rmse': float(best_model['rmse']),
            'mape': float(best_model['mape']),
            'is_ensemble': is_ensemble_winner,
            'ensemble_details': {
                'type': best_model.get('ensemble_type'),
                'components': best_model.get('component_models', [])
            } if is_ensemble_winner else None
        },
        'second_best_model': {
            'name': second_best_model['model_name'],
            'rmse': float(second_best_model['rmse']),
            'mape': float(second_best_model['mape']),
            'is_ensemble': 'ensemble_type' in second_best_model if isinstance(second_best_model, dict) else False
        } if second_best_model else None
    }
    
    # Сохранение в JSON
    comparison_file = os.path.join(task_folder, 'model_comparison.json')
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    
    # Сохранение прогнозов лучшей модели с датами
    from datetime import timedelta
    last_date = df.index[-1]
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                   periods=forecast_days, 
                                   freq='D')
    
    predictions_file = os.path.join(task_folder, 'best_model_predictions.csv')
    predictions_df = pd.DataFrame({
        'date': forecast_dates,
        'day': range(1, forecast_days + 1),
        'predicted_price': best_model['predictions']
    })
    predictions_df.to_csv(predictions_file, index=False)
    
    print(f"\n🥇 Лучшая модель: {best_model['model_name']}")
    print(f"   RMSE: {best_model['rmse']:.2f}, MAPE: {best_model['mape']:.2f}%")
    
    if second_best_model:
        print(f"\n🥈 Вторая лучшая модель: {second_best_model['model_name']}")
        print(f"   RMSE: {second_best_model['rmse']:.2f}, MAPE: {second_best_model['mape']:.2f}%")
    
    return best_model, second_best_model, comparison_data
