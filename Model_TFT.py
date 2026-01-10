import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, MultiHeadAttention, LayerNormalization
import warnings
warnings.filterwarnings('ignore')

def create_sequences(data, seq_length):
    """Создание последовательностей для обучения"""
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

def train_and_predict_tft(df: pd.DataFrame, forecast_days: int):
    """
    Упрощенная TFT (Temporal Fusion Transformer) модель
    Использует LSTM + Attention механизм
    """
    # Используем только цену закрытия
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]
    data = close_series.values.flatten().reshape(-1, 1)
    
    # Нормализация данных
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    
    # Параметры
    seq_length = 60
    
    # Создание последовательностей
    X, y = create_sequences(data_scaled, seq_length)
    
    # Разделение на train/test (80/20)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Построение упрощенной TFT модели с attention
    inputs = Input(shape=(seq_length, 1))
    
    # LSTM слои
    lstm_out = LSTM(64, return_sequences=True)(inputs)
    lstm_out = Dropout(0.2)(lstm_out)
    
    # Multi-head attention
    attention_out = MultiHeadAttention(num_heads=4, key_dim=16)(lstm_out, lstm_out)
    attention_out = LayerNormalization()(attention_out + lstm_out)
    
    # Финальные слои
    lstm_out2 = LSTM(32, return_sequences=False)(attention_out)
    lstm_out2 = Dropout(0.2)(lstm_out2)
    outputs = Dense(1)(lstm_out2)
    
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mse')
    
    # Обучение модели с оптимизированными параметрами
    early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    model.fit(X_train, y_train, batch_size=16, epochs=50, verbose=0, 
              validation_split=0.15, callbacks=[early_stop])
    
    # Прогноз на тестовой выборке
    test_predictions_scaled = model.predict(X_test, verbose=0)
    test_predictions = scaler.inverse_transform(test_predictions_scaled).flatten()
    test_actual = scaler.inverse_transform(y_test).flatten()
    
    # Метрики на тестовой выборке
    rmse = np.sqrt(mean_squared_error(test_actual, test_predictions))
    mape = mean_absolute_percentage_error(test_actual, test_predictions) * 100
    
    # Прогноз на будущее
    last_sequence = data_scaled[-seq_length:]
    future_predictions = []
    
    for _ in range(forecast_days):
        pred_scaled = model.predict(last_sequence.reshape(1, seq_length, 1), verbose=0)
        future_predictions.append(pred_scaled[0, 0])
        last_sequence = np.append(last_sequence[1:], pred_scaled)
    
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1)).flatten()
    
    return {
        'model_name': 'TFT',
        'predictions': future_predictions,
        'rmse': rmse,
        'mape': mape,
        'test_predictions': test_predictions,
        'test_actual': test_actual
    }
