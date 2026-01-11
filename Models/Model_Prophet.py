import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

def train_and_predict_prophet(df: pd.DataFrame, forecast_days: int):
    """
    Prophet модель для прогнозирования цен акций
    """
    # Подготовка данных для Prophet (нужны колонки ds и y)
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    
    # Убираем timezone из индекса если есть
    index_for_prophet = df.index
    if hasattr(index_for_prophet, 'tz') and index_for_prophet.tz is not None:
        index_for_prophet = index_for_prophet.tz_localize(None)
    
    prophet_df = pd.DataFrame({
        'ds': index_for_prophet,
        'y': close_series.values.flatten()
    })
    
    # Разделяем на train/test (80/20)
    train_size = int(len(prophet_df) * 0.8)
    train_df = prophet_df[:train_size]
    test_df = prophet_df[train_size:]
    
    # Обучаем Prophet модель с оптимизированными параметрами
    model = Prophet(
        daily_seasonality=True,
        yearly_seasonality=True,
        weekly_seasonality=True,
        changepoint_prior_scale=0.05,  # Гибкость тренда
        seasonality_prior_scale=10.0,   # Сила сезонности
        seasonality_mode='multiplicative'  # Мультипликативная сезонность
    )
    model.fit(train_df)
    
    # Прогноз на тестовой выборке
    test_predictions = model.predict(test_df[['ds']])['yhat'].values
    test_actual = test_df['y'].values
    
    # Метрики на тестовой выборке
    rmse = np.sqrt(mean_squared_error(test_actual, test_predictions))
    mape = mean_absolute_percentage_error(test_actual, test_predictions) * 100
    
    # Прогноз на будущее
    full_model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    full_model.fit(prophet_df)
    
    future = full_model.make_future_dataframe(periods=forecast_days)
    forecast = full_model.predict(future)
    future_predictions = forecast['yhat'].values[-forecast_days:]
    
    return {
        'model_name': 'Prophet',
        'predictions': future_predictions,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': test_actual
    }
