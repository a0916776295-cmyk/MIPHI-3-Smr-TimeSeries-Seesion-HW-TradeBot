import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(series, period=14):
    """Расчет индекса относительной силы (RSI)"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
    rs = gain / (loss + 1e-8)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50).values.flatten()

def create_sequences(data, seq_length):
    """Создание последовательностей для обучения"""
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

def train_and_predict_gru(df: pd.DataFrame, forecast_days: int):
    """
    GRU модель для прогнозирования цен акций
    """
    # Используем несколько признаков для лучшего прогноза
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    
    # Добавляем расширенный набор признаков
    close_values = close_series.values.flatten()
    features = pd.DataFrame({
        'Close': close_values,
        'Returns': close_series.pct_change().fillna(0).values.flatten(),
        'MA7': close_series.rolling(window=7, min_periods=1).mean().values.flatten(),
        'MA21': close_series.rolling(window=21, min_periods=1).mean().values.flatten(),
        'MA50': close_series.rolling(window=50, min_periods=1).mean().values.flatten(),
        'Lag1': close_series.shift(1).bfill().values.flatten(),
        'Lag3': close_series.shift(3).bfill().values.flatten(),
        'Lag7': close_series.shift(7).bfill().values.flatten(),
        'Volatility7': close_series.rolling(window=7, min_periods=1).std().fillna(0).values.flatten(),
        'Volatility21': close_series.rolling(window=21, min_periods=1).std().fillna(0).values.flatten(),
        'RSI': calculate_rsi(close_series, 14),
    })
    
    data = features.values
    
    # Нормализация данных
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Отдельный скейлер для цены закрытия
    price_scaler = MinMaxScaler()
    price_data = close_series.values.flatten().reshape(-1, 1)
    price_scaler.fit(price_data)
    
    # Параметры
    seq_length = 90  # Увеличиваем до 90 дней для лучшего контекста
    
    # Создание последовательностей
    X, y = create_sequences(data_scaled, seq_length)
    
    # Разделение на train/test (80/20)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Построение улучшенной GRU модели
    n_features = data_scaled.shape[1]
    model = Sequential([
        GRU(128, return_sequences=True, input_shape=(seq_length, n_features)),
        Dropout(0.3),
        GRU(64, return_sequences=True),
        Dropout(0.3),
        GRU(32, return_sequences=False),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1)
    ])
    
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss='mse')
    
    # Обучение модели с улучшенными callbacks
    early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)
    reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=0.00001)
    model.fit(X_train, y_train, batch_size=16, epochs=200, verbose=0, 
              validation_split=0.15, callbacks=[early_stop, reduce_lr])
    
    # Прогноз на тестовой выборке
    test_predictions_scaled = model.predict(X_test, verbose=0)
    test_predictions = price_scaler.inverse_transform(test_predictions_scaled).flatten()
    
    # Извлекаем только цену закрытия из y_test
    test_actual_prices = []
    for i in range(len(y_test)):
        test_actual_prices.append(y_test[i][0])
    test_actual = price_scaler.inverse_transform(np.array(test_actual_prices).reshape(-1, 1)).flatten()
    
    # Метрики на тестовой выборке
    rmse = np.sqrt(mean_squared_error(test_actual, test_predictions))
    mape = mean_absolute_percentage_error(test_actual, test_predictions) * 100
    
    # Прогноз на будущее с добавлением реалистичной волатильности
    last_sequence = data_scaled[-seq_length:]
    future_predictions_scaled = []
    
    # Вычисляем историческую волатильность
    returns = close_series.pct_change().dropna()
    historical_volatility = np.std(returns)
    
    # Адаптивный коэффициент шума в зависимости от волатильности
    if historical_volatility < 0.015:  # Низкая волатильность (<1.5%)
        noise_factor = 2.5
    elif historical_volatility < 0.03:  # Средняя волатильность (1.5-3%)
        noise_factor = 2.0
    else:  # Высокая волатильность (>3%)
        noise_factor = 1.5
    
    print(f"GRU: Historical volatility: {historical_volatility:.4f}, Noise factor: {noise_factor}")
    
    current_sequence = last_sequence.copy()
    for i in range(forecast_days):
        pred_scaled = model.predict(current_sequence.reshape(1, seq_length, n_features), verbose=0)[0, 0]
        
        # Добавляем стохастический компонент
        noise = np.random.normal(0, historical_volatility * noise_factor)
        
        # Применяем шум в нормализованном пространстве
        pred_with_noise = pred_scaled + noise * 0.5
        pred_with_noise = np.clip(pred_with_noise, 0, 1)
        
        future_predictions_scaled.append(pred_with_noise)
        
        # Обновляем последовательность
        new_row = current_sequence[-1].copy()
        new_row[0] = pred_with_noise
        if i > 0:
            new_row[1] = (pred_with_noise - future_predictions_scaled[i-1]) / (future_predictions_scaled[i-1] + 1e-8)
        current_sequence = np.vstack([current_sequence[1:], new_row])
    
    future_predictions = price_scaler.inverse_transform(np.array(future_predictions_scaled).reshape(-1, 1)).flatten()
    print(f"GRU: Prediction range: {future_predictions.min():.2f} - {future_predictions.max():.2f}")
    
    return {
        'model_name': 'GRU',
        'predictions': future_predictions,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': test_actual
    }
