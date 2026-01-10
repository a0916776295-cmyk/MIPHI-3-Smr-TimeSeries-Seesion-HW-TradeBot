import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

def create_features(close_series, window=60):
    """Создание признаков для Ridge Regression"""
    features_list = []
    targets = []
    
    close_values = close_series.values.flatten()
    
    for i in range(window, len(close_values)):
        # Берем последние window дней как признаки
        feature_row = []
        
        # Исторические цены (лаги)
        for lag in [1, 3, 7, 14, 21, 30]:
            if i - lag >= 0:
                feature_row.append(close_values[i - lag])
        
        # Скользящие средние
        feature_row.append(np.mean(close_values[max(0, i-7):i]))  # MA7
        feature_row.append(np.mean(close_values[max(0, i-21):i]))  # MA21
        
        # Волатильность
        if i >= 7:
            feature_row.append(np.std(close_values[i-7:i]))
        else:
            feature_row.append(0)
        
        # Returns
        if i > 0:
            feature_row.append((close_values[i] - close_values[i-1]) / close_values[i-1])
        else:
            feature_row.append(0)
        
        features_list.append(feature_row)
        targets.append(close_values[i])
    
    return np.array(features_list), np.array(targets)

def train_and_predict_ridge(df: pd.DataFrame, forecast_days: int):
    """
    Ridge Regression модель для прогнозирования цен акций
    """
    # Используем только цену закрытия
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    
    # Создаем признаки
    X, y = create_features(close_series, window=60)
    
    # Разделение на train/test (80/20)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Нормализация признаков
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Обучение Ridge Regression модели с оптимизированным alpha
    model = Ridge(alpha=0.5, max_iter=1000)  # Уменьшаем регуляризацию для лучшей подгонки
    model.fit(X_train_scaled, y_train)
    
    # Прогноз на тестовой выборке
    test_predictions = model.predict(X_test_scaled)
    
    # Метрики на тестовой выборке
    rmse = np.sqrt(mean_squared_error(y_test, test_predictions))
    mape = mean_absolute_percentage_error(y_test, test_predictions) * 100
    
    # Прогноз на будущее
    close_values = close_series.values.flatten()
    future_predictions = []
    
    # Вычисляем историческую волатильность для добавления шума
    returns = close_series.pct_change().dropna()
    historical_volatility = np.std(returns)
    
    # Адаптивный коэффициент шума
    if historical_volatility < 0.015:
        noise_factor = 2.5
    elif historical_volatility < 0.03:
        noise_factor = 2.0
    else:
        noise_factor = 1.5
    
    print(f"Ridge: Historical volatility: {historical_volatility:.4f}, Noise factor: {noise_factor}")
    
    # Используем последние данные для прогноза
    current_data = close_values.copy()
    
    for i in range(forecast_days):
        # Создаем признаки для текущего шага
        feature_row = []
        
        # Лаги
        for lag in [1, 3, 7, 14, 21, 30]:
            if len(current_data) - lag >= 0:
                feature_row.append(current_data[-lag])
        
        # MA7 и MA21
        feature_row.append(np.mean(current_data[-7:]))
        feature_row.append(np.mean(current_data[-21:]))
        
        # Волатильность
        feature_row.append(np.std(current_data[-7:]))
        
        # Returns
        feature_row.append((current_data[-1] - current_data[-2]) / current_data[-2])
        
        # Нормализация и предсказание
        feature_scaled = scaler.transform([feature_row])
        pred = model.predict(feature_scaled)[0]
        
        # Добавляем стохастический компонент
        noise = np.random.normal(0, historical_volatility * noise_factor)
        pred_with_noise = pred * (1 + noise)
        
        future_predictions.append(pred_with_noise)
        
        # Обновляем данные для следующего шага
        current_data = np.append(current_data, pred_with_noise)
    
    future_predictions = np.array(future_predictions)
    print(f"Ridge: Prediction range: {future_predictions.min():.2f} - {future_predictions.max():.2f}")
    
    return {
        'model_name': 'Ridge',
        'predictions': future_predictions,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': y_test
    }
