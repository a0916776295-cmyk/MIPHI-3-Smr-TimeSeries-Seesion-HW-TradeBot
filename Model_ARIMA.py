import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

def train_and_predict_arima(df: pd.DataFrame, forecast_days: int):
    """
    ARIMA модель для прогнозирования цен акций
    """
    # Используем только цену закрытия
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    data = close_series.values.flatten()
    
    # Разделяем на train/test (80/20)
    train_size = int(len(data) * 0.8)
    train, test = data[:train_size], data[train_size:]
    
    # Обучаем ARIMA модель с оптимизированными параметрами (p=7, d=1, q=2)
    model = ARIMA(train, order=(7, 1, 2))
    model_fit = model.fit()
    
    # Прогноз на тестовой выборке
    test_predictions = model_fit.forecast(steps=len(test))
    
    # Метрики на тестовой выборке
    rmse = np.sqrt(mean_squared_error(test, test_predictions))
    mape = mean_absolute_percentage_error(test, test_predictions) * 100
    
    # Прогноз на будущее
    full_model = ARIMA(data, order=(7, 1, 2))
    full_model_fit = full_model.fit()
    future_predictions = full_model_fit.forecast(steps=forecast_days)
    
    return {
        'model_name': 'ARIMA',
        'predictions': future_predictions,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': test
    }
