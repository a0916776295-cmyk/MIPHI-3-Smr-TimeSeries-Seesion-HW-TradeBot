import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(series, period=14):
    """Расчет RSI"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50).values.flatten()

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

def train_and_predict_gru(df: pd.DataFrame, forecast_days: int):
    """Оптимизированная GRU модель"""
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    
    # Расширенный набор признаков
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
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    price_scaler = MinMaxScaler()
    price_data = close_values.reshape(-1, 1)
    price_scaler.fit(price_data)
    
    # Оптимизированные параметры
    seq_length = 90
    X, y = create_sequences(data_scaled, seq_length)
    
    train_size = int(len(X) * 0.85)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Оптимизированная архитектура GRU
    n_features = data_scaled.shape[1]
    model = Sequential([
        GRU(256, return_sequences=True, input_shape=(seq_length, n_features)),
        BatchNormalization(),
        Dropout(0.3),
        GRU(128, return_sequences=True),
        BatchNormalization(),
        Dropout(0.3),
        GRU(64, return_sequences=False),
        BatchNormalization(),
        Dropout(0.2),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dense(1)
    ])
    
    optimizer = Adam(learning_rate=0.0005, clipnorm=1.0)
    model.compile(optimizer=optimizer, loss='huber', metrics=['mae'])
    
    early_stop = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=0.00001)
    
    model.fit(X_train, y_train, batch_size=8, epochs=200, verbose=0,
              validation_split=0.15, callbacks=[early_stop, reduce_lr])
    
    # Метрики БЕЗ шума
    test_predictions_scaled = model.predict(X_test, verbose=0)
    test_predictions = price_scaler.inverse_transform(test_predictions_scaled).flatten()
    
    test_actual_prices = [y_test[i][0] for i in range(len(y_test))]
    test_actual = price_scaler.inverse_transform(np.array(test_actual_prices).reshape(-1, 1)).flatten()
    
    rmse = np.sqrt(mean_squared_error(test_actual, test_predictions))
    mape = mean_absolute_percentage_error(test_actual, test_predictions) * 100
    
    print(f"GRU_OPT: RMSE={rmse:.2f}, MAPE={mape:.2f}%")
    
    # Прогноз БЕЗ шума
    last_sequence = data_scaled[-seq_length:]
    future_predictions = []
    
    current_sequence = last_sequence.copy()
    for i in range(forecast_days):
        pred_scaled = model.predict(current_sequence.reshape(1, seq_length, n_features), verbose=0)[0, 0]
        pred_scaled = np.clip(pred_scaled, 0, 1)
        future_predictions.append(pred_scaled)
        
        new_row = current_sequence[-1].copy()
        new_row[0] = pred_scaled
        if i > 0:
            new_row[1] = (pred_scaled - future_predictions[i-1]) / (future_predictions[i-1] + 1e-8)
        current_sequence = np.vstack([current_sequence[1:], new_row])
    
    future_predictions = price_scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1)).flatten()
    
    # Добавляем шум ТОЛЬКО для визуализации (30% от волатильности)
    returns = close_series.pct_change().dropna()
    historical_volatility = np.std(returns)
    noise_factor = 0.3  # 30% от исторической волатильности
    
    future_predictions_visual = future_predictions * (1 + np.random.normal(0, historical_volatility * noise_factor, len(future_predictions)))
    
    return {
        'model_name': 'GRU_OPT',
        'predictions': future_predictions_visual,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': test_actual
    }
