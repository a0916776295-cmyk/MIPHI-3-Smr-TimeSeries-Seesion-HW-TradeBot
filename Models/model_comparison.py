import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Импорт всех моделей
from .Model_ARIMA import train_and_predict_arima
from .Model_SARIMA import train_and_predict_sarima
from .Model_Prophet import train_and_predict_prophet
from .Model_LSTM import train_and_predict_lstm
from .Model_LSTM_optimized import train_and_predict_lstm as train_and_predict_lstm_opt
from .Model_GRU import train_and_predict_gru
from .Model_GRU_optimized import train_and_predict_gru as train_and_predict_gru_opt
from .Model_TFT import train_and_predict_tft
from .Model_Autoformer import train_and_predict_autoformer
from .Model_FEDformer import train_and_predict_fedformer
from .Model_Ridge import train_and_predict_ridge
from .Model_RandomForest import train_and_predict_randomforest

# Новые Transformer-based модели
try:
    from .Model_Transformer import train_transformer_model
    TRANSFORMER_AVAILABLE = True
    print("✅ Transformer модель успешно импортирована")
except ImportError as e:
    TRANSFORMER_AVAILABLE = False
    print(f"❌ Transformer модель не доступна: {e}")

try:
    from .Model_Informer import train_informer_model
    INFORMER_AVAILABLE = True
    print("✅ Informer модель успешно импортирована")
except ImportError as e:
    INFORMER_AVAILABLE = False
    print(f"❌ Informer модель не доступна: {e}")

# Ensemble методы
try:
    from .Model_Ensemble import create_ensemble_predictions
    ENSEMBLE_AVAILABLE = True
    print("✅ Ensemble методы успешно импортированы")
except ImportError as e:
    ENSEMBLE_AVAILABLE = False
    print(f"❌ Ensemble методы не доступны: {e}")

try:
    from .Model_XGBoost import train_and_predict_xgboost
    XGBOOST_AVAILABLE = True
    print("✅ XGBoost успешно импортирован")
except ImportError as e:
    XGBOOST_AVAILABLE = False
    print(f"❌ XGBoost не установлен: {e}")

try:
    from .Model_CatBoost import train_and_predict_catboost
    CATBOOST_AVAILABLE = True
    print("✅ CatBoost успешно импортирован")
except ImportError as e:
    CATBOOST_AVAILABLE = False
    print(f"❌ CatBoost не установлен: {e}")

def validate_prediction_sanity(predictions, current_price, model_name):
    """
    Проверка прогнозов на реалистичность
    Возвращает (is_valid, penalty_score, issues)
    """
    issues = []
    penalty_score = 0
    
    # 1. КРИТИЧЕСКИЙ: Проверка на отрицательные цены - ПОЛНЫЙ ЗАПРЕТ
    negative_prices = predictions[predictions < 0]
    if len(negative_prices) > 0:
        issues.append(f"КРИТИЧНО: Отрицательные цены: {len(negative_prices)} значений")
        penalty_score += 10000  # КРИТИЧЕСКИЙ штраф - полное исключение
    
    # 2. КРИТИЧЕСКИЙ: Проверка на экстремальные изменения (более 20% за день)
    daily_changes = []
    prev_price = current_price
    for price in predictions:
        if prev_price > 0:
            change_pct = abs(price - prev_price) / prev_price
            daily_changes.append(change_pct)
            if change_pct > 0.2:  # 20% изменение за день - уже подозрительно
                penalty_score += 500
            if change_pct > 0.5:  # 50% изменение за день - критично
                penalty_score += 5000
        prev_price = price
    
    max_daily_change = max(daily_changes) if daily_changes else 0
    if max_daily_change > 0.5:
        issues.append(f"КРИТИЧНО: Экстремальные изменения: до {max_daily_change*100:.1f}% за день")
    elif max_daily_change > 0.2:
        issues.append(f"Подозрительные изменения: до {max_daily_change*100:.1f}% за день")
    
    # 3. КРИТИЧЕСКИЙ: Проверка на нереальную волатильность
    price_range = predictions.max() - predictions.min()
    range_vs_current = price_range / current_price
    if range_vs_current > 5.0:  # Диапазон больше чем в 5 раз - критично
        issues.append(f"КРИТИЧНО: Экстремальная волатильность: диапазон {range_vs_current:.1f}x от текущей цены")
        penalty_score += 5000
    elif range_vs_current > 2.0:  # Диапазон больше чем в 2 раза - подозрительно
        issues.append(f"Высокая волатильность: диапазон {range_vs_current:.1f}x от текущей цены")
        penalty_score += 100
    
    # 4. Проверка на монотонность (подозрительно если все цены одинаковые или строго возрастают/убывают)
    unique_values = len(set(predictions.round(2)))
    if unique_values <= max(2, len(predictions) // 10):
        issues.append("Подозрительно низкое разнообразие прогнозов")
        penalty_score += 20
    
    is_valid = penalty_score < 100  # Строгая фильтрация: штраф должен быть минимальным
    
    if issues:
        print(f"⚠️ {model_name} - проблемы с реалистичностью (штраф {penalty_score}):")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print(f"✅ {model_name} - прогноз выглядит реалистично")
    
    return is_valid, penalty_score, issues

def calculate_enhanced_score(result, current_price):
    """
    Расчет улучшенной оценки модели с учетом реалистичности
    """
    rmse = result['rmse']
    mape = result['mape']
    predictions = result['predictions']
    model_name = result['model_name']
    
    # Проверяем реалистичность
    is_valid, penalty, issues = validate_prediction_sanity(predictions, current_price, model_name)
    
    # Базовая оценка (чем меньше, тем лучше)
    base_score = rmse * 0.7 + mape * 0.3  # Взвешенная оценка RMSE и MAPE
    
    # Добавляем штраф за нереалистичность
    final_score = base_score + penalty
    
    result['enhanced_score'] = final_score
    result['sanity_check'] = {
        'is_valid': is_valid,
        'penalty': penalty,
        'issues': issues
    }
    
    return final_score

def compare_all_models(df: pd.DataFrame, forecast_days: int, task_folder: str, fast_mode: bool = False):
    """
    Сравнение всех моделей и выбор лучшей (включая новые Transformer и Ensemble модели)
    
    Args:
        df: DataFrame с историческими данными
        forecast_days: Количество дней для прогноза  
        task_folder: Папка для сохранения результатов
        fast_mode: Если True, использует только быстрые модели (ARIMA, SARIMA, Ridge, RandomForest)
    """
    if fast_mode:
        print("⚡ БЫСТРЫЙ РЕЖИМ: Используются только легкие модели")
        models = [
            ('ARIMA', train_and_predict_arima),
            ('SARIMA', train_and_predict_sarima), 
            ('Ridge', train_and_predict_ridge),
            ('RandomForest', train_and_predict_randomforest),
        ]
        if XGBOOST_AVAILABLE:
            models.append(('XGBoost', train_and_predict_xgboost))
            print("✅ XGBoost добавлен в быстрый режим")
    else:
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
    current_price = df['Close'].iloc[-1]  # Текущая цена для проверок
    
    print(f"📊 Текущая цена: ${current_price:.2f}")
    print(f"📈 Период прогноза: {forecast_days} дней")
    print("=" * 60)
    
    for i, (model_name, model_func) in enumerate(models, 1):
        try:
            print(f"\n🔄 Обучение модели {model_name} ({i}/{len(models)})...")
            result = model_func(df, forecast_days)
            
            # Вычисляем улучшенную оценку с проверками реалистичности
            enhanced_score = calculate_enhanced_score(result, current_price)
            
            results.append(result)
            
            # Показываем детальную информацию
            is_valid = result['sanity_check']['is_valid']
            validity_icon = "✅" if is_valid else "❌"
            
            print(f"   {validity_icon} RMSE: {result['rmse']:.2f} | MAPE: {result['mape']:.2f}% | Оценка: {enhanced_score:.1f}")
            
            # Показываем диапазон прогнозов
            pred_min, pred_max = result['predictions'].min(), result['predictions'].max()
            print(f"   📊 Диапазон прогноза: ${pred_min:.2f} - ${pred_max:.2f}")
            
        except Exception as e:
            error_msg = str(e)[:100] + ("..." if len(str(e)) > 100 else "")
            print(f"❌ Ошибка в модели {model_name}: {error_msg}")
            print(f"   Тип ошибки: {type(e).__name__}")
            # Можно добавить детальный лог если нужно
            # import traceback
            # traceback.print_exc()
    
    if not results:
        print("\n❌ КРИТИЧЕСКАЯ ОШИБКА: Ни одна модель не смогла обучиться")
        print("   Возможные причины:")
        print("   • Проблемы с данными")
        print("   • Недостаточно исторических данных")
        print("   • Системные ошибки в библиотеках")
        raise Exception("Ни одна модель не смогла обучиться успешно")
    
    print(f"\n✅ Успешно обучено {len(results)} из {len(models)} моделей")
    
    # Сортировка моделей по улучшенной оценке (с учетом реалистичности)
    print("\n" + "=" * 60)
    print("🏆 ИТОГОВОЕ РАНЖИРОВАНИЕ МОДЕЛЕЙ:")
    print("=" * 60)
    
    sorted_results = sorted(results, key=lambda x: x['enhanced_score'])
    
    for i, result in enumerate(sorted_results[:5]):  # Показываем топ-5
        rank_icon = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
        validity = "✅" if result['sanity_check']['is_valid'] else "❌ НЕРЕАЛИСТИЧНО"
        print(f"{rank_icon} {result['model_name']:15} | Оценка: {result['enhanced_score']:6.1f} | {validity}")
    
    print("=" * 60)
    
    # Создаем ensemble модели ТОЛЬКО из реалистичных моделей
    ensemble_results = []
    if ENSEMBLE_AVAILABLE and len(results) >= 2:
        # Фильтруем только реалистичные модели для ensemble
        valid_models = [r for r in results if r.get('sanity_check', {}).get('is_valid', False)]
        print(f"\n🤖 Создание Ensemble моделей...")
        print(f"🧪 Создание ensemble из {len(valid_models)} реалистичных моделей...")
        
        if len(valid_models) >= 2:
            try:
                ensemble_results = create_ensemble_predictions(valid_models)
                if ensemble_results:
                    # КРИТИЧНО: Валидируем каждую ensemble модель
                    validated_ensemble = []
                    for ensemble_result in ensemble_results:
                        final_score = calculate_enhanced_score(ensemble_result, current_price)
                        
                        # Проверяем, что ensemble модель реалистична
                        if ensemble_result.get('sanity_check', {}).get('is_valid', False):
                            validated_ensemble.append(ensemble_result)
                            print(f"✅ {ensemble_result['model_name']}: валидация пройдена")
                        else:
                            issues = ensemble_result.get('sanity_check', {}).get('issues', [])
                            print(f"❌ {ensemble_result['model_name']}: ОТКЛОНЕНА - {'; '.join(issues)}")
                    
                    if validated_ensemble:
                        # Добавляем только валидные ensemble результаты
                        all_results = results + validated_ensemble
                        sorted_results = sorted(all_results, key=lambda x: x['rmse'])
                        print(f"✅ Добавлено {len(validated_ensemble)} проверенных ensemble моделей")
                    else:
                        print("⚠️ Все ensemble модели отклонены из-за нереалистичности")
                        sorted_results = sorted(results, key=lambda x: x['rmse'])
                else:
                    print("❌ Не удалось создать ensemble модели")
                    sorted_results = sorted(results, key=lambda x: x['rmse'])
            except Exception as e:
                print(f"❌ Ошибка при создании ensemble: {str(e)}")
                sorted_results = sorted(results, key=lambda x: x['rmse'])
        else:
            print("❌ Недостаточно реалистичных моделей для создания ensemble")
            sorted_results = sorted(results, key=lambda x: x['rmse'])
    else:
        print("🔍 Ensemble не создается: недостаточно моделей или не доступен")
        sorted_results = sorted(results, key=lambda x: x['rmse'])
    
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
                'enhanced_score': float(r.get('enhanced_score', r['rmse'] * 0.7 + r['mape'] * 0.3)),
                'is_realistic': r.get('sanity_check', {}).get('is_valid', True),
                'sanity_penalty': float(r.get('sanity_check', {}).get('penalty', 0)),
                'sanity_issues': r.get('sanity_check', {}).get('issues', []),
                'is_ensemble': 'ensemble_type' in r if isinstance(r, dict) else False,
                'prediction_range': {
                    'min': float(r['predictions'].min()),
                    'max': float(r['predictions'].max())
                }
            }
            for r in sorted_results
        ],
        'best_model': {
            'name': best_model['model_name'],
            'rmse': float(best_model['rmse']),
            'mape': float(best_model['mape']),
            'enhanced_score': float(best_model.get('enhanced_score', best_model['rmse'] * 0.7 + best_model['mape'] * 0.3)),
            'is_realistic': best_model.get('sanity_check', {}).get('is_valid', True),
            'sanity_issues': best_model.get('sanity_check', {}).get('issues', []),
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
    
    # Финальное объявление победителя
    validity_status = "✅ РЕАЛИСТИЧНАЯ" if best_model.get('sanity_check', {}).get('is_valid', True) else "⚠️ ТРЕБУЕТ ВНИМАНИЯ"
    enhanced_score = best_model.get('enhanced_score', best_model['rmse'] * 0.7 + best_model['mape'] * 0.3)
    print(f"\n🏆 ПОБЕДИТЕЛЬ: {best_model['model_name']} - {validity_status}")
    print(f"   📊 RMSE: {best_model['rmse']:.2f} | MAPE: {best_model['mape']:.2f}%")
    print(f"   🎯 Итоговая оценка: {enhanced_score:.1f}")
    
    pred_range = f"${best_model['predictions'].min():.2f} - ${best_model['predictions'].max():.2f}"
    print(f"   📈 Диапазон прогноза: {pred_range}")
    
    sanity_issues = best_model.get('sanity_check', {}).get('issues', [])
    if sanity_issues:
        print(f"   ⚠️ Замечания: {'; '.join(sanity_issues)}")
    
    if second_best_model:
        validity_status2 = "✅" if second_best_model.get('sanity_check', {}).get('is_valid', True) else "⚠️"
        enhanced_score2 = second_best_model.get('enhanced_score', second_best_model['rmse'] * 0.7 + second_best_model['mape'] * 0.3)
        print(f"\n🥈 Альтернатива: {second_best_model['model_name']} {validity_status2}")
        print(f"   📊 RMSE: {second_best_model['rmse']:.2f} | MAPE: {second_best_model['mape']:.2f}%")
        print(f"   🎯 Итоговая оценка: {enhanced_score2:.1f}")
    
    return best_model, second_best_model, comparison_data
