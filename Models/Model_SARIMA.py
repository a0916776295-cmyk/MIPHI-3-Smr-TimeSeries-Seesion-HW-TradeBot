import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

def train_and_predict_sarima(df: pd.DataFrame, forecast_days: int):
    """
    SARIMA модель для прогнозирования цен акций
    """
    # Используем только цену закрытия
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    data = close_series.values.flatten()
    
    # Разделяем на train/test (80/20)
    train_size = int(len(data) * 0.8)
    train, test = data[:train_size], data[train_size:]
    
    # Обучаем SARIMA модель с оптимизированными параметрами
    # Используем сезонность 7 (недельный цикл)
    model = SARIMAX(train, order=(2, 1, 2), seasonal_order=(1, 1, 1, 7))
    model_fit = model.fit(disp=False, maxiter=200)
    
    # Прогноз на тестовой выборке
    test_predictions = model_fit.forecast(steps=len(test))
    
    # Метрики на тестовой выборке
    rmse = np.sqrt(mean_squared_error(test, test_predictions))
    mape = mean_absolute_percentage_error(test, test_predictions) * 100
    
    # Прогноз на будущее
    full_model = SARIMAX(data, order=(2, 1, 2), seasonal_order=(1, 1, 1, 7))
    full_model_fit = full_model.fit(disp=False, maxiter=200)
    future_predictions = full_model_fit.forecast(steps=forecast_days)
    
    return {
        'model_name': 'SARIMA',
        'predictions': future_predictions,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': test
    }
