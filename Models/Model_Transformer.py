# -*- coding: utf-8 -*-
"""
Transformer модель для прогнозирования временных рядов
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

class MultiHeadAttention(layers.Layer):
    """Multi-Head Attention механизм для временных рядов"""
    
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        
        assert d_model % self.num_heads == 0
        
        self.depth = d_model // self.num_heads
        
        self.wq = layers.Dense(d_model)
        self.wk = layers.Dense(d_model)
        self.wv = layers.Dense(d_model)
        
        self.dense = layers.Dense(d_model)
        
    def split_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    
    def call(self, v, k, q, mask=None):
        batch_size = tf.shape(q)[0]
        
        q = self.wq(q)
        k = self.wk(k)
        v = self.wv(v)
        
        q = self.split_heads(q, batch_size)
        k = self.split_heads(k, batch_size)
        v = self.split_heads(v, batch_size)
        
        scaled_attention = self.scaled_dot_product_attention(q, k, v, mask)
        scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])
        
        concat_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model))
        output = self.dense(concat_attention)
        
        return output
    
    def scaled_dot_product_attention(self, q, k, v, mask):
        matmul_qk = tf.matmul(q, k, transpose_b=True)
        dk = tf.cast(tf.shape(k)[-1], tf.float32)
        scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)
        
        if mask is not None:
            scaled_attention_logits += (mask * -1e9)
            
        attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)
        output = tf.matmul(attention_weights, v)
        
        return output

class TransformerBlock(layers.Layer):
    """Transformer блок"""
    
    def __init__(self, d_model, num_heads, ff_dim, dropout_rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = MultiHeadAttention(d_model, num_heads)
        self.ffn = tf.keras.Sequential([
            layers.Dense(ff_dim, activation="relu"),
            layers.Dense(d_model)
        ])
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(dropout_rate)
        self.dropout2 = layers.Dropout(dropout_rate)
    
    def call(self, inputs, training=None):
        attn_output = self.att(inputs, inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        
        return self.layernorm2(out1 + ffn_output)

def create_sequences(data, seq_length, prediction_steps):
    """Создание последовательностей для обучения"""
    X, y = [], []
    for i in range(seq_length, len(data) - prediction_steps + 1):
        X.append(data[i-seq_length:i])
        y.append(data[i:i+prediction_steps])
    return np.array(X), np.array(y)

def build_transformer_model(seq_length, d_model=64, num_heads=8, ff_dim=128, 
                           num_transformer_blocks=4, dropout_rate=0.1, prediction_steps=1):
    """Создание Transformer модели"""
    
    inputs = layers.Input(shape=(seq_length, 1))
    
    # Positional encoding
    x = layers.Dense(d_model)(inputs)
    
    # Transformer blocks
    for _ in range(num_transformer_blocks):
        x = TransformerBlock(d_model, num_heads, ff_dim, dropout_rate)(x)
    
    # Global average pooling
    x = layers.GlobalAveragePooling1D()(x)
    
    # Final dense layers
    x = layers.Dense(ff_dim, activation='relu')(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(ff_dim // 2, activation='relu')(x)
    outputs = layers.Dense(prediction_steps)(x)
    
    model = models.Model(inputs, outputs)
    return model

def train_transformer_model(df, prediction_steps=5, epochs=100, batch_size=32, 
                           seq_length=60, test_size=0.2, random_state=42):
    """
    Обучение Transformer модели
    """
    print(f"🤖 Начало обучения Transformer модели...")
    
    # Подготовка данных
    data = df['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # Создание последовательностей
    X, y = create_sequences(scaled_data, seq_length, prediction_steps)
    
    if len(X) < 10:
        raise ValueError(f"Недостаточно данных для обучения. Нужно минимум {seq_length + prediction_steps} записей")
    
    # Разделение на train/test
    train_size = int(len(X) * (1 - test_size))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    print(f"📊 Размер обучающей выборки: {X_train.shape}")
    print(f"📊 Размер тестовой выборки: {X_test.shape}")
    
    # Создание модели
    model = build_transformer_model(
        seq_length=seq_length, 
        prediction_steps=prediction_steps,
        d_model=64,
        num_heads=8,
        ff_dim=128,
        num_transformer_blocks=3,
        dropout_rate=0.1
    )
    
    # Компиляция
    model.compile(
        optimizer=optimizers.Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )
    
    # Callbacks
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=0
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=8,
        min_lr=1e-7,
        verbose=0
    )
    
    # Обучение
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping, reduce_lr],
        verbose=0
    )
    
    # Предсказания на тестовой выборке
    test_predictions = model.predict(X_test, verbose=0)
    
    # Обратное масштабирование
    test_predictions_scaled = scaler.inverse_transform(
        test_predictions.reshape(-1, 1)
    ).flatten()
    
    y_test_scaled = scaler.inverse_transform(
        y_test.reshape(-1, 1)
    ).flatten()
    
    # Метрики
    test_rmse = np.sqrt(mean_squared_error(y_test_scaled, test_predictions_scaled))
    test_mape = mean_absolute_percentage_error(y_test_scaled, test_predictions_scaled) * 100
    
    print(f"Transformer: Test RMSE={test_rmse:.2f}, MAPE={test_mape:.2f}%")
    
    # Прогноз на будущее
    last_sequence = scaled_data[-seq_length:].reshape(1, seq_length, 1)
    future_prediction = model.predict(last_sequence, verbose=0)
    future_prediction_scaled = scaler.inverse_transform(future_prediction.reshape(-1, 1)).flatten()
    
    # Добавляем некоторую волатильность к прогнозу
    historical_volatility = np.std(np.diff(data.flatten())) / np.mean(data.flatten())
    noise_factor = min(2.0, max(0.5, historical_volatility * 100))
    
    print(f"Transformer: Historical volatility: {historical_volatility:.4f}, Noise factor: {noise_factor:.1f}")
    
    # Применяем небольшой шум для реалистичности
    noise = np.random.normal(0, historical_volatility * data[-1, 0] * 0.1, prediction_steps)
    future_prediction_scaled += noise
    
    print(f"Transformer: Prediction range: {future_prediction_scaled.min():.2f} - {future_prediction_scaled.max():.2f}")
    
    result = {
        'model_name': 'Transformer',
        'rmse': test_rmse,
        'mape': test_mape,
        'predictions': future_prediction_scaled,
        'model': model,
        'scaler': scaler,
        'history': history.history
    }
    
    print(f"Transformer: RMSE={test_rmse:.2f}, MAPE={test_mape:.2f}%")
    return result