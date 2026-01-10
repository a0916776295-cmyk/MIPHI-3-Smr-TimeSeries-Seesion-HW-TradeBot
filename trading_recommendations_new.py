import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from datetime import timedelta

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
    Рассчитывает активную торговую стратегию с учетом локальных экстремумов
    
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
    
    # Анализируем общий тренд
    price_change = (predictions[-1] - current_price) / current_price
    
    print(f"📊 Анализ тренда: текущая цена ${current_price:.2f}, конечная ${predictions[-1]:.2f}")
    print(f"📈 Общее изменение: {price_change*100:.2f}%")
    
    # Находим все локальные экстремумы с повышенной чувствительностью
    local_min_indices, local_max_indices = find_local_extrema(predictions, order=1)
    
    print(f"🔍 Найдено локальных минимумов: {len(local_min_indices)}")
    print(f"🔍 Найдено локальных максимумов: {len(local_max_indices)}")
    
    if len(local_min_indices) == 0 and len(local_max_indices) == 0:
        print("❌ Локальные экстремумы не найдены - стратегия недоступна")
        return recommendations, 0, trades
    
    # Создаем единый список всех торговых точек
    trading_points = []
    
    # Добавляем локальные минимумы как точки покупки
    for idx in local_min_indices:
        price = predictions[idx]
        date = forecast_dates[idx]
        trading_points.append({
            'day': idx + 1,
            'date': date.strftime('%Y-%m-%d'),
            'price': price,
            'type': 'buy',
            'strength': current_price - price  # Чем больше падение, тем лучше покупка
        })
    
    # Добавляем локальные максимумы как точки продажи
    for idx in local_max_indices:
        price = predictions[idx]
        date = forecast_dates[idx]
        trading_points.append({
            'day': idx + 1,
            'date': date.strftime('%Y-%m-%d'),
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
        
        if point['type'] == 'buy' and profit_potential > min_profit_threshold:
            # Покупка в локальном минимуме
            if cash > 0:
                shares_to_buy = int(cash / price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    shares += shares_to_buy
                    cash -= cost
                    total_invested += cost
                    
                    recommendations.append({
                        'day': point['day'],
                        'date': point['date'],
                        'action': f'ПОКУПАТЬ {shares_to_buy} акций',
                        'price': f'${price:.2f}',
                        'reason': f'Локальный минимум - потенциальный рост {profit_potential*100:.1f}%'
                    })
                    
                    trades.append({
                        'type': 'buy',
                        'shares': shares_to_buy,
                        'price': price,
                        'day': point['day']
                    })
        
        elif point['type'] == 'sell' and profit_potential > min_profit_threshold:
            # Продажа в локальном максимуме
            if shares > 0:
                # Обычная продажа имеющихся акций
                revenue = shares * price
                cash += revenue
                
                recommendations.append({
                    'day': point['day'],
                    'date': point['date'],
                    'action': f'ПРОДАВАТЬ {shares} акций',
                    'price': f'${price:.2f}',
                    'reason': f'Локальный максимум - фиксация прибыли {profit_potential*100:.1f}%'
                })
                
                trades.append({
                    'type': 'sell',
                    'shares': shares,
                    'price': price,
                    'day': point['day']
                })
                
                shares = 0
            
            elif cash > 0 and price_change < 0:
                # Короткая продажа, если общий тренд нисходящий
                shares_to_short = int((cash * 0.5) / price)  # Используем 50% от доступных средств
                if shares_to_short > 0:
                    short_shares += shares_to_short
                    
                    recommendations.append({
                        'day': point['day'],
                        'date': point['date'],
                        'action': f'КОРОТКАЯ ПРОДАЖА {shares_to_short} акций',
                        'price': f'${price:.2f}',
                        'reason': f'Локальный максимум при нисходящем тренде - заработок на падении'
                    })
                    
                    trades.append({
                        'type': 'short_sell',
                        'shares': shares_to_short,
                        'price': price,
                        'day': point['day']
                    })
    
    # Закрываем позиции в конце периода
    final_price = predictions[-1]
    final_date = forecast_dates[-1].strftime('%Y-%m-%d')
    
    # Продаем оставшиеся акции
    if shares > 0:
        revenue = shares * final_price
        cash += revenue
        
        recommendations.append({
            'day': len(predictions),
            'date': final_date,
            'action': f'ФИНАЛЬНАЯ ПРОДАЖА {shares} акций',
            'price': f'${final_price:.2f}',
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
    Генерирует текстовое описание рекомендаций с учетом активной торговли
    """
    text = f"💼 **АКТИВНАЯ ТОРГОВАЯ СТРАТЕГИЯ ДЛЯ {ticker}**\n\n"
    text += f"💰 Начальные инвестиции: ${initial_investment:.2f}\n"
    
    if expected_profit != 0:
        text += f"📈 Ожидаемая прибыль: ${expected_profit:.2f} ({profit_percent:+.2f}%)\n\n"
        
        if profit_percent > 5:
            text += "🚀 **ОТЛИЧНАЯ ВОЗМОЖНОСТЬ!** Высокодоходная стратегия\n\n"
        elif profit_percent > 2:
            text += "✅ **ХОРОШАЯ ВОЗМОЖНОСТЬ** Прибыльная торговля\n\n"
        elif profit_percent > 0.5:
            text += "⚡ **УМЕРЕННАЯ ПРИБЫЛЬ** Стабильный доход\n\n"
        elif profit_percent > 0:
            text += "💡 **НЕБОЛЬШАЯ ПРИБЫЛЬ** Минимальный риск\n\n"
        else:
            text += "⚠️ **РИСКИ ПРЕВЫШАЮТ ДОХОДНОСТЬ** Осторожно!\n\n"
    else:
        text += "📊 Прогнозная прибыль: $0.00 (0.00%)\n\n"
        text += "⚠️ **СЛОЖНЫЕ РЫНОЧНЫЕ CONDITIONS** Избегать торговли\n\n"
    
    if len(recommendations) == 0:
        text += "❌ **НЕТ ТОРГОВЫХ ВОЗМОЖНОСТЕЙ**\n"
        text += "Прогноз не показывает возможностей для прибыльной торговли.\n"
        text += "Рекомендуется выбрать другой актив или дождаться лучших условий.\n"
    else:
        text += "🎯 **АКТИВНАЯ ТОРГОВАЯ СТРАТЕГИЯ**\n\n"
        text += "💡 *Стратегия использует локальные колебания цены для извлечения прибыли даже при общем нисходящем тренде*\n\n"
        
        text += "📋 **ТОРГОВЫЕ СИГНАЛЫ:**\n\n"
        
        all_actions = sorted(recommendations, key=lambda x: x['day'])
        for i, rec in enumerate(all_actions, 1):
            if "ПОКУПАТЬ" in rec['action']:
                emoji = "🟢"
            elif "КОРОТКАЯ" in rec['action']:
                emoji = "📉"
            elif "ПРОДАВАТЬ" in rec['action'] or "ФИНАЛЬНАЯ" in rec['action']:
                emoji = "🔴"
            elif "ПОКРЫТЬ" in rec['action']:
                emoji = "📈"
            else:
                emoji = "🟡"
                
            text += f"{emoji} **День {rec['day']} ({rec['date']})**\n"
            text += f"   {rec['action']} по цене {rec['price']}\n"
            text += f"   💭 {rec['reason']}\n\n"
        
        # Подсчитываем типы операций
        buy_actions = [r for r in recommendations if 'ПОКУПАТЬ' in r['action']]
        sell_actions = [r for r in recommendations if any(word in r['action'] for word in ['ПРОДАВАТЬ', 'ФИНАЛЬНАЯ'])]
        short_actions = [r for r in recommendations if 'КОРОТКАЯ' in r['action']]
        
        if buy_actions or sell_actions or short_actions:
            text += "📊 **СТАТИСТИКА СТРАТЕГИИ:**\n"
            if buy_actions:
                text += f"• Покупок: {len(buy_actions)}\n"
            if sell_actions:
                text += f"• Продаж: {len(sell_actions)}\n"
            if short_actions:
                text += f"• Коротких продаж: {len(short_actions)}\n"
                text += "• 🎯 **Заработок на падении цен!**\n"
            text += "\n"
    
    text += "🎓 **ПРИНЦИПЫ АКТИВНОЙ ТОРГОВЛИ:**\n"
    text += "• 📈 Покупка в локальных минимумах\n"
    text += "• 📉 Продажа в локальных максимумах\n"
    text += "• 🩳 Короткие продажи при прогнозе падения\n"
    text += "• 💎 Фиксация прибыли в ключевых точках\n"
    text += "• ⚡ Использование волатильности рынка\n\n"
    
    text += "⚠️ **ВАЖНЫЕ НАПОМИНАНИЯ:**\n"
    text += "• Стратегия основана на ML-прогнозе\n"
    text += "• Используйте стоп-лоссы для защиты\n"
    text += "• Рынок может вести себя непредсказуемо\n"
    text += "• Не инвестируйте критично важные средства"
    
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