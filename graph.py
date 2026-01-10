import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from datetime import timedelta

# Отключаем сглаживание линий глобально
plt.rcParams['lines.antialiased'] = False
plt.rcParams['path.simplify'] = False

def generate_graph(df: pd.DataFrame, ticker: str, folder: str = ".") -> str:
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Close'], linewidth=1.5)
    plt.title(f"{ticker} — График цены за 2 года")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.grid(True)

    img_path = os.path.join(folder, f"{ticker}_graph.png")
    plt.savefig(img_path, dpi=200)
    plt.close()

    return img_path

def generate_forecast_graph_zoomed(df: pd.DataFrame, ticker: str, predictions: np.ndarray, 
                                  model_name: str, folder: str = ".") -> str:
    """
    Создает увеличенный график с последними 60 днями и прогнозом БЕЗ сглаживания
    """
    plt.figure(figsize=(16, 7))
    
    df_recent = df.tail(60)
    
    # Исторические данные
    plt.plot(df_recent.index, df_recent['Close'], label='Последние 60 дней', 
             color='#2E86AB', linewidth=2.5, alpha=0.9, solid_capstyle='butt', solid_joinstyle='miter')
    
    # Создаем даты для прогноза
    last_date = df.index[-1]
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                   periods=len(predictions), 
                                   freq='D')
    
    # Прогноз БЕЗ сглаживания
    plt.plot(forecast_dates, predictions, label=f'Прогноз ({model_name})', 
             color='#E63946', linewidth=2.5, linestyle='-', alpha=0.9,
             solid_capstyle='butt', solid_joinstyle='miter')
    
    # Соединяем последнюю точку истории с первой точкой прогноза
    plt.plot([df.index[-1], forecast_dates[0]], 
             [df['Close'].iloc[-1], predictions[0]], 
             color='#F77F00', linewidth=2, linestyle=':', alpha=0.7)
    
    # Добавляем заливку под прогнозом
    plt.fill_between(forecast_dates, predictions, alpha=0.2, color='#E63946')
    
    # Вертикальная линия разделения
    plt.axvline(x=last_date, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)
    plt.text(last_date, plt.ylim()[1]*0.95, 'Сегодня', 
             ha='right', va='top', fontsize=10, color='gray')
    
    # Аннотации
    plt.annotate(f'${predictions[0]:.2f}', 
                xy=(forecast_dates[0], predictions[0]),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                fontsize=9)
    
    plt.annotate(f'${predictions[-1]:.2f}', 
                xy=(forecast_dates[-1], predictions[-1]),
                xytext=(10, -10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                fontsize=9)
    
    plt.title(f"{ticker} — Детальный прогноз на {len(predictions)} дней ({model_name})", 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Дата", fontsize=13, fontweight='bold')
    plt.ylabel("Цена ($)", fontsize=13, fontweight='bold')
    plt.legend(loc='best', fontsize=11, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.xticks(rotation=45, ha='right')
    
    img_path = os.path.join(folder, f"{ticker}_{model_name}_forecast_zoomed.png")
    plt.savefig(img_path, dpi=200, bbox_inches='tight')
    plt.close()
    
    return img_path

def generate_forecast_graph(df: pd.DataFrame, ticker: str, predictions: np.ndarray, 
                           model_name: str, folder: str = ".") -> str:
    """
    Создает график с историческими данными и прогнозом БЕЗ сглаживания
    """
    plt.figure(figsize=(16, 7))
    
    # Исторические данные БЕЗ сглаживания
    plt.plot(df.index, df['Close'], label='Исторические данные (2 года)', 
             color='#2E86AB', linewidth=2.5, alpha=0.9,
             solid_capstyle='butt', solid_joinstyle='miter')
    
    # Создаем даты для прогноза
    last_date = df.index[-1]
    forecast_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                   periods=len(predictions), 
                                   freq='D')
    
    # Прогноз БЕЗ сглаживания
    plt.plot(forecast_dates, predictions, label=f'Прогноз ({model_name})', 
             color='#E63946', linewidth=2.5, linestyle='-', alpha=0.9,
             solid_capstyle='butt', solid_joinstyle='miter')
    
    # Соединяем последнюю точку истории с первой точкой прогноза
    plt.plot([df.index[-1], forecast_dates[0]], 
             [df['Close'].iloc[-1], predictions[0]], 
             color='#F77F00', linewidth=2, linestyle=':', alpha=0.7)
    
    # Добавляем заливку под прогнозом
    plt.fill_between(forecast_dates, predictions, alpha=0.2, color='#E63946')
    
    # Вертикальная линия разделения
    plt.axvline(x=last_date, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)
    plt.text(last_date, plt.ylim()[1]*0.95, 'Сегодня', 
             ha='right', va='top', fontsize=10, color='gray')
    
    # Аннотации
    plt.annotate(f'${predictions[0]:.2f}', 
                xy=(forecast_dates[0], predictions[0]),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                fontsize=9)
    
    plt.annotate(f'${predictions[-1]:.2f}', 
                xy=(forecast_dates[-1], predictions[-1]),
                xytext=(10, -10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                fontsize=9)
    
    plt.title(f"{ticker} — Прогноз цены на {len(predictions)} дней ({model_name})", 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Дата", fontsize=13, fontweight='bold')
    plt.ylabel("Цена ($)", fontsize=13, fontweight='bold')
    plt.legend(loc='best', fontsize=11, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.xticks(rotation=45, ha='right')
    
    img_path = os.path.join(folder, f"{ticker}_{model_name}_forecast_full.png")
    plt.savefig(img_path, dpi=200, bbox_inches='tight')
    plt.close()
    
    return img_path
