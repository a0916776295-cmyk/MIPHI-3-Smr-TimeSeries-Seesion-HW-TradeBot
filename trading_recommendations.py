import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from datetime import timedelta
import os

def convert_numpy_types_in_recommendations(recommendations):
    """
    Преобразует numpy типы данных в торговых рекомендациях для корректной JSON сериализации
    """
    cleaned_recommendations = []
    for rec in recommendations:
        cleaned_rec = {}
        for key, value in rec.items():
            if hasattr(value, 'item'):  # numpy скаляр
                cleaned_rec[key] = value.item()
            elif hasattr(value, 'tolist'):  # numpy массив
                cleaned_rec[key] = value.tolist()
            else:
                cleaned_rec[key] = value
        cleaned_recommendations.append(cleaned_rec)
    return cleaned_recommendations

def find_local_extrema(predictions, order=3):
    """
    Находит локальные минимумы и максимумы в прогнозе
    
    Args:
        predictions: массив предсказанных цен
        order: количество соседних точек для сравнения
    
    Returns:
        local_min_indices: индексы локальных минимумов
        local_max_indices: индексы локальных максимумов
    """
    # Находим локальные минимумы
    local_min_indices = argrelextrema(predictions, np.less, order=order)[0]
    
    # Находим локальные максимумы
    local_max_indices = argrelextrema(predictions, np.greater, order=order)[0]
    
    return local_min_indices, local_max_indices

def calculate_trading_strategy(predictions, forecast_dates, initial_investment, 
                               current_price, min_profit_threshold=0.005):
    """
    Рассчитывает торговую стратегию на основе прогноза с учетом локальных колебаний
    
    Args:
        predictions: массив предсказанных цен
        forecast_dates: даты прогноза
        initial_investment: начальная сумма инвестиций
        current_price: текущая цена акции
        min_profit_threshold: минимальный порог прибыли (0.5% по умолчанию)
    
    Returns:
        recommendations: список рекомендаций с датами
        expected_profit: ожидаемая прибыль
        trades: список сделок
    """
    recommendations = []
    trades = []
    
    # Преобразуем в numpy array если нужно
    if not isinstance(predictions, np.ndarray):
        predictions = np.array(predictions)
    
    # Анализируем общий тренд
    price_change = (predictions[-1] - current_price) / current_price
    
    print(f"📊 Анализ тренда: текущая цена ${current_price:.2f}, конечная ${predictions[-1]:.2f}")
    print(f"📈 Общее изменение: {price_change*100:.2f}%")
    
    # Находим все локальные экстремумы с более чувствительными параметрами
    local_min_indices, local_max_indices = find_local_extrema(predictions, order=1)
    
    # Если нет четких экстремумов, создаем их искусственно
    if len(local_min_indices) == 0 and len(local_max_indices) == 0:
        # Ищем простые точки поворота
        for i in range(1, len(predictions) - 1):
            if predictions[i] > predictions[i-1] and predictions[i] > predictions[i+1]:
                local_max_indices = np.append(local_max_indices, i)
            elif predictions[i] < predictions[i-1] and predictions[i] < predictions[i+1]:
                local_min_indices = np.append(local_min_indices, i)
    
    # Создаем полную стратегию торговли независимо от общего тренда
    trading_opportunities = []
    
    # Добавляем стартовую точку
    trading_opportunities.append({
        'day': 0,
        'price': current_price,
        'type': 'start',
        'date': forecast_dates[0] - pd.Timedelta(days=1)
    })
    
    # Добавляем локальные минимумы (точки покупки)
    for idx in local_min_indices:
        if idx < len(predictions):
            trading_opportunities.append({
                'day': idx + 1,
                'price': predictions[idx],
                'type': 'buy',
                'date': forecast_dates[idx]
            })
    
    # Добавляем локальные максимумы (точки продажи)
    for idx in local_max_indices:
        if idx < len(predictions):
            trading_opportunities.append({
                'day': idx + 1,
                'price': predictions[idx],
                'type': 'sell',
                'date': forecast_dates[idx]
            })
    
    # Добавляем конечную точку
    trading_opportunities.append({
        'day': len(predictions),
        'price': predictions[-1],
        'type': 'end',
        'date': forecast_dates[-1]
    })
    
    # Сортируем по дням
    trading_opportunities.sort(key=lambda x: x['day'])
    
    print(f"🎯 Найдено торговых возможностей: {len(trading_opportunities)}")
    
    # Симулируем активную торговую стратегию
    cash = initial_investment
    shares = 0
    total_trades = 0
    successful_trades = 0
    
    # Анализируем возможности для прибыли
    for i in range(len(trading_opportunities) - 1):
        current_opp = trading_opportunities[i]
        next_opp = trading_opportunities[i + 1] if i + 1 < len(trading_opportunities) else None
        
        if not next_opp:
            continue
            
        price_diff = (next_opp['price'] - current_opp['price']) / current_opp['price']
        
        # Возможность покупки (цена растет дальше)
        if price_diff > min_profit_threshold and cash > 0:
            shares_to_buy = cash / current_opp['price']
            shares += shares_to_buy
            
            # Рассчитываем ожидаемую прибыль от этой операции
            expected_profit_per_operation = (next_opp["price"] - current_opp['price']) * shares_to_buy
            
            recommendations.append({
                'date': current_opp['date'].strftime('%d.%m.%Y'),
                'day': current_opp['day'],
                'action': '🟢 ПОКУПАТЬ',
                'price': current_opp['price'],
                'shares': shares_to_buy,
                'expected_profit': expected_profit_per_operation,
                'reason': f'Прогнозируется рост до ${next_opp["price"]:.2f} (+{price_diff*100:.1f}%)'
            })
            
            trades.append({
                'date': current_opp['date'],
                'action': 'BUY',
                'price': current_opp['price'],
                'shares': shares_to_buy,
                'amount': cash
            })
            
            cash = 0
            total_trades += 1
            
        # Возможность продажи (цена падает дальше или достигнут максимум)
        elif shares > 0 and (price_diff < -min_profit_threshold or current_opp['type'] == 'sell'):
            sell_value = shares * current_opp['price']
            
            # Рассчитываем прибыль от последней покупки
            last_buy = [t for t in trades if t['action'] == 'BUY'][-1] if [t for t in trades if t['action'] == 'BUY'] else None
            
            # Рассчитываем прибыль от продажи
            if last_buy:
                sell_profit = (current_opp['price'] - last_buy['price']) * shares
                profit = (current_opp['price'] - last_buy['price']) / last_buy['price']
                
                if profit > 0:
                    successful_trades += 1
                    reason = f'Фиксация прибыли (+{profit*100:.1f}%)'
                else:
                    reason = f'Стоп-лосс ({profit*100:.1f}%)'
                    
                if price_diff < -min_profit_threshold:
                    reason += f', прогнозируется падение до ${next_opp["price"]:.2f}'
            else:
                sell_profit = 0
                reason = f'Продажа по цене ${current_opp["price"]:.2f}'
            
            recommendations.append({
                'date': current_opp['date'].strftime('%d.%m.%Y'),
                'day': current_opp['day'],
                'action': '🔴 ПРОДАВАТЬ',
                'price': current_opp['price'],
                'shares': shares,
                'expected_profit': sell_profit,
                'reason': reason
            })
            
            trades.append({
                'date': current_opp['date'],
                'action': 'SELL',
                'price': current_opp['price'],
                'shares': shares,
                'amount': sell_value
            })
            
            cash = sell_value
            shares = 0
            total_trades += 1
            
        # Возможность короткой продажи (при нисходящем тренде)
        elif price_diff < -min_profit_threshold * 2 and cash > 0:
            # Эмулируем короткую продажу
            short_shares = cash / current_opp['price']
            expected_short_profit = (current_opp['price'] - next_opp['price']) * short_shares
            
            recommendations.append({
                'date': current_opp['date'].strftime('%d.%m.%Y'),
                'day': current_opp['day'],
                'action': '📉 КОРОТКАЯ ПРОДАЖА',
                'price': current_opp['price'],
                'shares': short_shares,
                'expected_profit': expected_short_profit,
                'reason': f'Прогнозируется падение до ${next_opp["price"]:.2f} ({price_diff*100:.1f}%)'
            })
            
            # Покрываем короткую позицию
            if next_opp:
                cover_value = short_shares * next_opp['price']
                profit = cash - cover_value
                
                recommendations.append({
                    'date': next_opp['date'].strftime('%d.%m.%Y'),
                    'day': next_opp['day'],
                    'action': '📈 ПОКРЫТЬ КОРОТКУЮ',
                    'price': next_opp['price'],
                    'expected_profit': profit,
                    'reason': f'Прибыль от короткой продажи: ${profit:.2f}'
                })
                
                cash += profit
                total_trades += 2
                successful_trades += 1 if profit > 0 else 0
    
    # Закрываем позицию в конце, если есть акции
    if shares > 0:
        final_value = shares * predictions[-1]
        last_buy = [t for t in trades if t['action'] == 'BUY'][-1] if [t for t in trades if t['action'] == 'BUY'] else None
        
        # Рассчитываем прибыль от финальной продажи
        if last_buy:
            final_profit = (predictions[-1] - last_buy['price']) * shares
            profit = (predictions[-1] - last_buy['price']) / last_buy['price']
            reason = f'Закрытие позиции (+{profit*100:.1f}%)' if profit > 0 else f'Закрытие позиции ({profit*100:.1f}%)'
        else:
            final_profit = 0
            reason = 'Закрытие позиции'
            
        recommendations.append({
            'date': forecast_dates[-1].strftime('%d.%m.%Y'),
            'day': len(predictions),
            'action': '🔴 ФИНАЛЬНАЯ ПРОДАЖА',
            'price': predictions[-1],
            'shares': shares,
            'expected_profit': final_profit,
            'reason': reason
        })
        
        cash = final_value
        shares = 0
    
    # Рассчитываем итоговую прибыль
    final_value = cash
    expected_profit = final_value - initial_investment
    profit_percent = (expected_profit / initial_investment) * 100
    
    print(f"💰 Торговая симуляция:")
    print(f"   Начальный капитал: ${initial_investment:.2f}")
    print(f"   Финальный капитал: ${final_value:.2f}")
    print(f"   Прибыль: ${expected_profit:.2f} ({profit_percent:.2f}%)")
    print(f"   Всего сделок: {total_trades}")
    print(f"   Успешных: {successful_trades}")
    
    # Очищаем рекомендации от numpy типов перед возвратом
    cleaned_recommendations = convert_numpy_types_in_recommendations(recommendations)
    
    return cleaned_recommendations, expected_profit, profit_percent, trades

def generate_brief_recommendations_text(recommendations, ticker):
    """
    Генерирует краткий формат торговых рекомендаций: дата-действие-цена-прибыль
    """
    if not recommendations:
        return f"❌ **НЕТ ТОРГОВЫХ СИГНАЛОВ ДЛЯ {ticker}**"
    
    text = f"💼 **ТОРГОВЫЙ ПЛАН ДЛЯ {ticker}:**\n\n"
    
    for i, rec in enumerate(recommendations, 1):
        action_emoji = "🟢 ПОКУПАТЬ" if "ПОКУПАТЬ" in rec['action'] else \
                      "🔴 ПРОДАВАТЬ" if "ПРОДАВАТЬ" in rec['action'] else \
                      "📦 ЗАКРЫТЬ ПОЗИЦИЮ" if "ФИНАЛЬНАЯ" in rec['action'] else rec['action']
        
        profit_text = ""
        if 'expected_profit' in rec and rec['expected_profit'] != 0:
            profit_sign = "+" if rec['expected_profit'] > 0 else ""
            profit_text = f" → {profit_sign}${rec['expected_profit']:.2f}"
        
        text += f"{i}. **{rec['date']}** - {action_emoji} по ${float(rec['price']):.2f}{profit_text}\n"
    
    return text

def generate_recommendations_text(recommendations, expected_profit, profit_percent, 
                                  initial_investment, ticker):
    """
    Генерирует текстовое описание рекомендаций
    """
    text = f"� **ТОРГОВЫЕ РЕКОМЕНДАЦИИ ДЛЯ {ticker}**\n\n"
    text += f"💰 Начальные инвестиции: ${initial_investment:.2f}\n"
    
    if expected_profit != 0:
        text += f"📈 Ожидаемая прибыль: ${expected_profit:.2f} ({profit_percent:+.2f}%)\n\n"
        
        if profit_percent > 2:
            text += "✅ **Стратегия высоко прибыльна!**\n\n"
        elif profit_percent > 0.5:
            text += "✅ **Стратегия потенциально прибыльна**\n\n"
        else:
            text += "⚠️ **Низкая доходность, высокие риски**\n\n"
    else:
        text += "📊 Прогнозная прибыль: $0.00 (0.00%)\n\n"
        text += "⚠️ **Рекомендуется воздержаться от активной торговли**\n\n"
    
    if len(recommendations) == 0:
        text += "❌ **НЕТ ЧЕТКИХ ТОРГОВЫХ СИГНАЛОВ**\n"
        text += "Прогноз не показывает явных возможностей для прибыльной торговли.\n"
        text += "Рекомендуется дождаться более благоприятных условий.\n"
    else:
        text += "📅 **ПЛАН ДЕЙСТВИЙ:**\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            emoji = "🟢" if "ПОКУПАТЬ" in rec['action'] else "🔴" if "ПРОДАВАТЬ" in rec['action'] else "🟡"
            text += f"{emoji} **{i}. День {rec['day']} ({rec['date']})**\n"
            text += f"   {rec['action']} по цене ${float(rec['price']):.2f}\n"
            
            # Отображаем ожидаемую прибыль для каждой операции
            if 'expected_profit' in rec and rec['expected_profit'] != 0:
                profit_sign = "+" if rec['expected_profit'] > 0 else ""
                text += f"   💰 Ожидаемая прибыль: {profit_sign}${rec['expected_profit']:.2f}\n"
            
            text += f"   💡 {rec['reason']}\n\n"
    
    text += "⚠️ **ВАЖНО:** Это автоматические рекомендации на основе прогноза. "
    text += "Реальные рыночные условия могут отличаться. Всегда консультируйтесь с финансовыми консультантами."
    
    return text

def save_recommendations_to_file(recommendations, expected_profit, profit_percent, 
                                initial_investment, ticker, task_folder):
    """
    Сохраняет рекомендации в файл
    """
    import os
    
    text = generate_recommendations_text(recommendations, expected_profit, profit_percent,
                                        initial_investment, ticker)
    
    file_path = os.path.join(task_folder, 'trading_recommendations.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Также сохраняем в CSV для анализа
    csv_path = os.path.join(task_folder, 'trading_recommendations.csv')
    df = pd.DataFrame(recommendations)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    
    return file_path, csv_path
