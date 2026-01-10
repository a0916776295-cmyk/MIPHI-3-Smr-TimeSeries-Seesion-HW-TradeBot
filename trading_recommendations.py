import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from datetime import timedelta

def find_local_extrema(predictions, order=3):
    """
    Находит локальные минимумы и максимумы в прогнозе
    
    Args:
        predictions: массив предсказанных цен (list или numpy array)
        order: количество соседних точек для сравнения
    
    Returns:
        local_min_indices: индексы локальных минимумов
        local_max_indices: индексы локальных максимумов
    """
    # Преобразуем в numpy array если получили список
    if isinstance(predictions, list):
        predictions = np.array(predictions)
        
    # Находим локальные минимумы
    local_min_indices = argrelextrema(predictions, np.less, order=order)[0]
    
    # Находим локальные максимумы
    local_max_indices = argrelextrema(predictions, np.greater, order=order)[0]
    
    return local_min_indices, local_max_indices

def calculate_trading_strategy(predictions, forecast_dates, initial_investment, 
                               current_price, min_profit_threshold=0.001):
    """
    Рассчитывает активную торговую стратегию с учетом локальных экстремумов
    
    Args:
        predictions: массив предсказанных цен
        forecast_dates: даты прогноза
        initial_investment: начальная сумма инвестиций
        current_price: текущая цена акции
        min_profit_threshold: минимальный порог прибыли (0.1% по умолчанию)
    
    Returns:
        recommendations: список рекомендаций с датами
        expected_profit: ожидаемая прибыль
        trades: список сделок
    """
    recommendations = []
    trades = []
    
    # Проверяем наличие данных
    if len(predictions) == 0:
        print("⚠️ Нет данных для анализа")
        return recommendations, 0.0, trades
    
    # Анализируем общий тренд
    price_change = (predictions[-1] - current_price) / current_price
    
    print(f"📊 Анализ тренда: текущая цена ${current_price:.2f}, конечная ${predictions[-1]:.2f}")
    print(f"📈 Общее изменение: {price_change*100:.2f}%")
    
    # Находим все локальные экстремумы с оптимальной чувствительностью
    # Начинаем с малой чувствительности для поиска большего количества точек
    local_min_indices, local_max_indices = find_local_extrema(predictions, order=1)
    
    # Если слишком много точек, повышаем order
    if len(local_min_indices) + len(local_max_indices) > 8:
        local_min_indices, local_max_indices = find_local_extrema(predictions, order=2)
        
    # Если слишком мало точек, понижаем порог (если еще не на минимуме)
    if len(local_min_indices) + len(local_max_indices) < 2:
        # Пробуем найти простые минимумы и максимумы в каждом окне
        window_size = max(3, len(predictions) // 4)
        for i in range(window_size, len(predictions) - window_size):
            # Проверяем локальные минимумы
            if predictions[i] < predictions[i-1] and predictions[i] < predictions[i+1]:
                if i not in local_min_indices:
                    local_min_indices = np.append(local_min_indices, i)
            # Проверяем локальные максимумы
            if predictions[i] > predictions[i-1] and predictions[i] > predictions[i+1]:
                if i not in local_max_indices:
                    local_max_indices = np.append(local_max_indices, i)
    
    print(f"🔍 Найдено локальных минимумов: {len(local_min_indices)}")
    print(f"🔍 Найдено локальных максимумов: {len(local_max_indices)}")
    
    # Дополнительно находим глобальные минимум и максимум если локальных мало
    if len(local_min_indices) == 0:
        global_min_idx = np.argmin(predictions)
        local_min_indices = np.array([global_min_idx])
        print(f"🔍 Добавлен глобальный минимум на дне {global_min_idx + 1}")
    
    if len(local_max_indices) == 0:
        global_max_idx = np.argmax(predictions)
        local_max_indices = np.array([global_max_idx])
        print(f"🔍 Добавлен глобальный максимум на дне {global_max_idx + 1}")
    
    # Если все еще нет экстремумов, создаем минимальную стратегию
    if len(local_min_indices) == 0 and len(local_max_indices) == 0:
        print("⚠️ Локальные экстремумы не найдены - создаем простую стратегию")
        
        # Создаем простую стратегию: купить сразу, продать в конце
        if price_change > 0.01:  # Если ожидаем рост более 1%
            shares_to_buy = initial_investment / current_price  # Покупаем дробные акции
            if shares_to_buy >= 0.1:  # Минимальное количество 0.1 акции
                cost = shares_to_buy * current_price
                final_value = shares_to_buy * predictions[-1]
                profit = final_value - cost
                
                recommendations.append({
                    'day': 1,
                    'date': forecast_dates[0].strftime('%Y-%m-%d') if hasattr(forecast_dates[0], 'strftime') else str(forecast_dates[0]),
                    'action': 'КУПИТЬ',
                    'shares': shares_to_buy,
                    'price': current_price,
                    'operation_profit': profit,
                    'reason': f'Простая стратегия - ожидаем рост {price_change*100:.1f}%'
                })
                
                recommendations.append({
                    'day': len(predictions),
                    'date': forecast_dates[-1].strftime('%Y-%m-%d') if hasattr(forecast_dates[-1], 'strftime') else str(forecast_dates[-1]),
                    'action': 'ПРОДАТЬ',
                    'shares': shares_to_buy,
                    'price': predictions[-1],
                    'operation_profit': profit,
                    'reason': f'Закрытие позиции с прибылью {profit:.2f}'
                })
                
                return recommendations, profit, []
    
    # Создаем единый список всех торговых точек
    trading_points = []
    
    # Добавляем локальные минимумы как точки покупки
    for idx in local_min_indices:
        price = predictions[idx]
        date = forecast_dates[idx]
        # Обрабатываем и строки и datetime объекты
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        trading_points.append({
            'day': idx + 1,
            'date': date_str,
            'price': price,
            'type': 'buy',
            'strength': current_price - price  # Чем больше падение, тем лучше покупка
        })
    
    # Добавляем локальные максимумы как точки продажи
    for idx in local_max_indices:
        price = predictions[idx]
        date = forecast_dates[idx]
        # Обрабатываем и строки и datetime объекты
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        trading_points.append({
            'day': idx + 1,
            'date': date_str,
            'price': price,
            'type': 'sell',
            'strength': price - current_price  # Чем больше рост, тем лучше продажа
        })
    
    # Сортируем точки по дням
    trading_points = sorted(trading_points, key=lambda x: x['day'])
    
    print(f"🎯 Всего торговых точек: {len(trading_points)}")
    
    # Симулируем активную торговлю
    cash = initial_investment
    shares = 0
    short_shares = 0  # Количество акций в короткой позиции
    total_invested = 0
    
    for point in trading_points:
        price = point['price']
        profit_potential = abs(point['strength']) / current_price
        
        if point['type'] == 'buy':
            # Покупка в локальном минимуме (используем все доступные средства)
            # Для дорогих акций разрешаем покупку дробных акций
            if cash >= price * 0.1:  # Можем купить минимум 0.1 акции
                shares_to_buy = cash / price  # Покупаем дробные акции
                if shares_to_buy >= 0.1:  # Минимальное количество 0.1 акции
                    cost = shares_to_buy * price
                    shares += shares_to_buy
                    cash -= cost
                    total_invested += cost
                    
                    # Находим следующий максимум для расчета потенциальной прибыли
                    next_max_price = predictions[-1]  # По умолчанию финальная цена
                    for future_point in trading_points:
                        if future_point['day'] > point['day'] and future_point['type'] == 'sell':
                            next_max_price = future_point['price']
                            break
                    
                    # Рассчитываем ожидаемую прибыль от операции
                    operation_profit = shares_to_buy * (next_max_price - price)
                    
                    recommendations.append({
                        'day': point['day'],
                        'date': point['date'],
                        'action': 'КУПИТЬ',
                        'shares': shares_to_buy,
                        'price': price,
                        'operation_profit': operation_profit,
                        'reason': f'Локальный минимум ${price:.2f} - покупка для роста до ${next_max_price:.2f}'
                    })
                    
                    trades.append({
                        'type': 'buy',
                        'shares': shares_to_buy,
                        'price': price,
                        'day': point['day']
                    })
        
        elif point['type'] == 'sell':
            # Продажа в локальном максимуме
            if shares > 0:
                # Обычная продажа всех имеющихся акций в максимуме
                revenue = shares * price
                # Находим цену последней покупки для расчета прибыли
                last_buy_price = 0
                for trade in reversed(trades):
                    if trade['type'] == 'buy':
                        last_buy_price = trade['price']
                        break
                
                operation_profit = shares * (price - last_buy_price) if last_buy_price > 0 else revenue - total_invested
                cash += revenue
                
                recommendations.append({
                    'day': point['day'],
                    'date': point['date'],
                    'action': 'ПРОДАТЬ',
                    'shares': shares,
                    'price': price,
                    'operation_profit': operation_profit,
                    'reason': f'Локальный максимум ${price:.2f} - фиксация прибыли (купили по ${last_buy_price:.2f})'
                })
                
                trades.append({
                    'type': 'sell',
                    'shares': shares,
                    'price': price,
                    'day': point['day']
                })
                
                shares = 0
                total_invested = 0  # Обнуляем инвестиции после продажи
    
    # Закрываем позиции в конце периода
    final_price = predictions[-1]
    final_date_obj = forecast_dates[-1]
    final_date = final_date_obj.strftime('%Y-%m-%d') if hasattr(final_date_obj, 'strftime') else str(final_date_obj)
    
    # Продаем оставшиеся акции
    if shares > 0:
        revenue = shares * final_price
        operation_profit = revenue - total_invested  # Финальная прибыль
        cash += revenue
        
        recommendations.append({
            'day': len(predictions),
            'date': final_date,
            'action': 'ПРОДАТЬ (финальная)',
            'shares': shares,
            'price': final_price,
            'operation_profit': operation_profit,
            'reason': 'Закрытие позиции в конце прогнозного периода'
        })
        
        trades.append({
            'type': 'sell',
            'shares': shares,
            'price': final_price,
            'day': len(predictions)
        })
    
    # Закрываем короткие позиции
    if short_shares > 0:
        cost_to_cover = short_shares * final_price
        cash -= cost_to_cover
        
        recommendations.append({
            'day': len(predictions),
            'date': final_date,
            'action': f'ПОКРЫТЬ КОРОТКУЮ ПОЗИЦИЮ {short_shares} акций',
            'price': f'${final_price:.2f}',
            'reason': 'Закрытие короткой позиции в конце периода'
        })
        
        trades.append({
            'type': 'cover_short',
            'shares': short_shares,
            'price': final_price,
            'day': len(predictions)
        })
    
    # Рассчитываем финальную прибыль
    expected_profit = cash - initial_investment
    
    print(f"💰 Результаты активной торговли:")
    print(f"   Начальный капитал: ${initial_investment:.2f}")
    print(f"   Финальный капитал: ${cash:.2f}")
    print(f"   Прибыль: ${expected_profit:.2f}")
    print(f"   Количество сделок: {len(trades)}")
    
    return recommendations, expected_profit, trades

def generate_recommendations_text(recommendations, expected_profit, profit_percent, 
                                  initial_investment, ticker):
    """
    Генерирует структурированное описание рекомендаций в стиле логирования
    """
    
    if not recommendations:
        return f"❌ НЕТ ТОРГОВЫХ ВОЗМОЖНОСТЕЙ ДЛЯ {ticker}"
    
    text = f"📈 ТОРГОВЫЕ РЕКОМЕНДАЦИИ ДЛЯ {ticker}\n\n"
    
    for rec in recommendations:
        date = rec.get('date', 'Дата не указана')
        action = rec.get('action', 'ОЖИДАТЬ')
        price = rec.get('price', 0)
        operation_profit = rec.get('operation_profit', 0)
        
        # Форматируем цену
        if isinstance(price, (int, float)):
            price_text = f"{price:.2f}"
        else:
            price_text = str(price).replace('$', '')
        
        # Форматируем прибыль
        profit_text = f"{operation_profit:.2f}" if operation_profit != 0 else "0.00"
        
        # Определяем действие и цветовое оформление в стиле логов
        if 'КУПИТЬ' in action or 'ПОКУПАТЬ' in action:
            action_code = "КУПИТЬ"
            # Красный цвет для покупки
            formatted_line = f"🔴 [ТОРГИ] {date} {ticker} {action_code} {price_text} прибыль:{profit_text}"
        elif 'ПРОДАТЬ' in action:
            action_code = "ПРОДАТЬ"
            # Зеленый цвет для продажи
            formatted_line = f"🟢 [ТОРГИ] {date} {ticker} {action_code} {price_text} прибыль:{profit_text}"
        elif 'ШОРТ' in action or 'КОРОТКАЯ' in action:
            action_code = "ПРОДАТЬ_КОРОТКО"
            # Зеленый цвет для продажи
            formatted_line = f"🟢 [ТОРГИ] {date} {ticker} {action_code} {price_text} прибыль:{profit_text}"
        else:
            action_code = "ДЕРЖАТЬ"
            # Обычный формат для ожидания
            formatted_line = f"⚪ [ТОРГИ] {date} {ticker} {action_code} {price_text} прибыль:{profit_text}"
        
        # Добавляем отформатированную строку
        text += f"{formatted_line}\n"
    
    # Итоговая прибыль
    text += f"\n💰 [ИТОГО] Общая_прибыль: {expected_profit:.2f}\n"
    
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

def get_trading_recommendations(predictions, forecast_dates, ticker, current_price, 
                               initial_investment=1000):
    """
    Основная функция для получения торговых рекомендаций с активной стратегией
    
    Args:
        predictions: массив предсказанных цен
        forecast_dates: даты прогноза
        ticker: тикер акции
        current_price: текущая цена акции
        initial_investment: начальная сумма инвестиций
        
    Returns:
        recommendations: список рекомендаций
        expected_profit: ожидаемая прибыль в долларах
        profit_percent: ожидаемая прибыль в процентах
        recommendations_text: текстовое описание рекомендаций
    """
    print(f"\n🔄 Генерируем активные торговые рекомендации для {ticker}")
    print(f"💰 Начальная инвестиция: ${initial_investment}")
    print(f"💲 Текущая цена: ${current_price:.2f}")
    
    # Рассчитываем стратегию
    recommendations, expected_profit, trades = calculate_trading_strategy(
        predictions, forecast_dates, initial_investment, current_price
    )
    
    # Рассчитываем процент прибыли
    profit_percent = (expected_profit / initial_investment) * 100 if initial_investment > 0 else 0
    
    print(f"📈 Ожидаемая прибыль: ${expected_profit:.2f} ({profit_percent:+.2f}%)")
    print(f"🎯 Количество торговых сигналов: {len(recommendations)}")
    
    # Генерируем текстовое описание
    recommendations_text = generate_recommendations_text(
        recommendations, expected_profit, profit_percent, initial_investment, ticker
    )
    
    return recommendations, expected_profit, profit_percent, recommendations_text