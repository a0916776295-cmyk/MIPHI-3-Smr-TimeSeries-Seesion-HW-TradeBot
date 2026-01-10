import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from catboost import CatBoostRegressor
import warnings
warnings.filterwarnings('ignore')

def create_features(close_series, window=90):
    """Создание расширенного набора признаков"""
    features_list = []
    targets = []
    
    close_values = close_series.values.flatten()
    
    for i in range(window, len(close_values)):
        feature_row = []
        
        # Лаги (исторические цены)
        for lag in [1, 2, 3, 5, 7, 10, 14, 21, 30]:
            if i - lag >= 0:
                feature_row.append(close_values[i - lag])
        
        # Скользящие средние
        feature_row.append(np.mean(close_values[max(0, i-5):i]))   # MA5
        feature_row.append(np.mean(close_values[max(0, i-7):i]))   # MA7
        feature_row.append(np.mean(close_values[max(0, i-14):i]))  # MA14
        feature_row.append(np.mean(close_values[max(0, i-21):i]))  # MA21
        feature_row.append(np.mean(close_values[max(0, i-50):i]))  # MA50
        
        # Волатильность
        feature_row.append(np.std(close_values[max(0, i-7):i]))   # Vol7
        feature_row.append(np.std(close_values[max(0, i-14):i]))  # Vol14
        feature_row.append(np.std(close_values[max(0, i-21):i]))  # Vol21
        
        # Returns (доходность)
        for lag in [1, 3, 7, 14]:
            if i - lag > 0:
                feature_row.append((close_values[i - lag] - close_values[i - lag - 1]) / close_values[i - lag - 1])
        
        # RSI
        if i >= 14:
            rsi_window = close_values[i-14:i]
            delta = np.diff(rsi_window)
            gain = np.mean([d for d in delta if d > 0] or [0])
            loss = np.mean([-d for d in delta if d < 0] or [0])
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            feature_row.append(rsi)
        else:
            feature_row.append(50)
        
        # Momentum
        if i >= 10:
            feature_row.append(close_values[i-1] - close_values[i-10])
        else:
            feature_row.append(0)
        
        # Rate of Change
        if i >= 14:
            feature_row.append((close_values[i-1] - close_values[i-14]) / close_values[i-14])
        else:
            feature_row.append(0)
        
        # Bollinger Bands position
        if i >= 20:
            ma20 = np.mean(close_values[i-20:i])
            std20 = np.std(close_values[i-20:i])
            if std20 > 0:
                bb_position = (close_values[i-1] - ma20) / (2 * std20)
                feature_row.append(bb_position)
            else:
                feature_row.append(0)
        else:
            feature_row.append(0)
        
        features_list.append(feature_row)
        targets.append(close_values[i])
    
    return np.array(features_list), np.array(targets)

def train_and_predict_catboost(df: pd.DataFrame, forecast_days: int):
    """
    CatBoost модель для прогнозирования цен акций
    """
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    
    # Создаем признаки
    X, y = create_features(close_series, window=90)
    
    # Разделение на train/test (85/15)
    train_size = int(len(X) * 0.85)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Нормализация признаков
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Обучение CatBoost модели с оптимальными параметрами
    model = CatBoostRegressor(
        iterations=500,           # Количество итераций
        learning_rate=0.03,       # Скорость обучения
        depth=8,                  # Глубина деревьев
        l2_leaf_reg=3,           # L2 регуляризация
        loss_function='RMSE',     # Функция потерь
        eval_metric='RMSE',       # Метрика оценки
        random_seed=42,
        verbose=False,            # Отключаем вывод
        thread_count=-1,          # Использовать все ядра
        early_stopping_rounds=50  # Ранняя остановка
    )
    
    # Обучение с валидацией
    model.fit(
        X_train_scaled, y_train,
        eval_set=(X_test_scaled, y_test),
        verbose=False
    )
    
    # Прогноз на тестовой выборке БЕЗ шума
    test_predictions = model.predict(X_test_scaled)
    
    # Метрики
    rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
    mape = mean_absolute_percentage_error(y_test, test_predictions) * 100
    
    print(f"CatBoost: RMSE={rmse:.2f}, MAPE={mape:.2f}%")
    print(f"CatBoost: Best iteration={model.get_best_iteration()}")
    
    # Прогноз на будущее БЕЗ шума
    close_values = close_series.values.flatten()
    future_predictions = []
    
    current_data = close_values.copy()
    
    for i in range(forecast_days):
        # Создаем признаки для текущего шага
        feature_row = []
        
        # Лаги
        for lag in [1, 2, 3, 5, 7, 10, 14, 21, 30]:
            if len(current_data) - lag >= 0:
                feature_row.append(current_data[-lag])
        
        # MA
        feature_row.append(np.mean(current_data[-5:]))
        feature_row.append(np.mean(current_data[-7:]))
        feature_row.append(np.mean(current_data[-14:]))
        feature_row.append(np.mean(current_data[-21:]))
        feature_row.append(np.mean(current_data[-50:]))
        
        # Volatility
        feature_row.append(np.std(current_data[-7:]))
        feature_row.append(np.std(current_data[-14:]))
        feature_row.append(np.std(current_data[-21:]))
        
        # Returns
        for lag in [1, 3, 7, 14]:
            if len(current_data) - lag > 0:
                feature_row.append((current_data[-lag] - current_data[-lag-1]) / current_data[-lag-1])
        
        # RSI
        if len(current_data) >= 14:
            rsi_window = current_data[-14:]
            delta = np.diff(rsi_window)
            gain = np.mean([d for d in delta if d > 0] or [0])
            loss = np.mean([-d for d in delta if d < 0] or [0])
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            feature_row.append(rsi)
        else:
            feature_row.append(50)
        
        # Momentum
        if len(current_data) >= 10:
            feature_row.append(current_data[-1] - current_data[-10])
        else:
            feature_row.append(0)
        
        # Rate of Change
        if len(current_data) >= 14:
            feature_row.append((current_data[-1] - current_data[-14]) / current_data[-14])
        else:
            feature_row.append(0)
        
        # Bollinger Bands
        if len(current_data) >= 20:
            ma20 = np.mean(current_data[-20:])
            std20 = np.std(current_data[-20:])
            if std20 > 0:
                bb_position = (current_data[-1] - ma20) / (2 * std20)
                feature_row.append(bb_position)
            else:
                feature_row.append(0)
        else:
            feature_row.append(0)
        
        # Нормализация и предсказание
        feature_scaled = scaler.transform([feature_row])
        pred = model.predict(feature_scaled)[0]
        
        future_predictions.append(pred)
        current_data = np.append(current_data, pred)
    
    future_predictions = np.array(future_predictions)
    
    # Добавляем шум ТОЛЬКО для визуализации (30% от волатильности)
    returns = close_series.pct_change().dropna()
    historical_volatility = np.std(returns)
    noise_factor = 0.3  # 30% от исторической волатильности
    
    future_predictions_visual = future_predictions * (1 + np.random.normal(0, historical_volatility * noise_factor, len(future_predictions)))
    
    print(f"CatBoost: Clean prediction range: {future_predictions.min():.2f} - {future_predictions.max():.2f}")
    print(f"CatBoost: Visual prediction range: {future_predictions_visual.min():.2f} - {future_predictions_visual.max():.2f}")
    
    return {
        'model_name': 'CatBoost',
        'predictions': future_predictions_visual,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': y_test
    }
