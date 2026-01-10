# -*- coding: utf-8 -*-
"""
Модуль для испытания прогнозов реальностью
Позволяет сравнивать прогнозы с фактическими данными
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from finance import get_finance_data
from LoggerModule import log_bot_action
import asyncio

# Хранилище активных тестов реальности
# Структура: {user_id: {"ticker": str, "target_date": str, "forecast": list, "forecast_dates": list, "amount": int, "model_name": str}}
reality_tests = {}

def save_reality_tests():
    """Сохранить активные тесты в файл"""
    print(f"💾 Попытка сохранить {len(reality_tests)} тестов в файл")
    try:
        with open('reality_tests.json', 'w', encoding='utf-8') as f:
            # Преобразуем numpy arrays в обычные списки для JSON
            tests_to_save = {}
            for user_id, test_data in reality_tests.items():
                test_copy = test_data.copy()
                if 'forecast' in test_copy and isinstance(test_copy['forecast'], np.ndarray):
                    test_copy['forecast'] = test_copy['forecast'].tolist()
                tests_to_save[user_id] = test_copy
            json.dump(tests_to_save, f, ensure_ascii=False, indent=2)
        print(f"✅ Тесты сохранены в файл reality_tests.json")
        log_bot_action("Reality tests saved to file")
    except Exception as e:
        print(f"❌ Ошибка при сохранении тестов: {str(e)}")
        import traceback
        traceback.print_exc()
        log_bot_action(f"Error saving reality tests: {str(e)}")

def load_reality_tests():
    """Загрузить активные тесты из файла"""
    global reality_tests
    try:
        if os.path.exists('reality_tests.json'):
            with open('reality_tests.json', 'r', encoding='utf-8') as f:
                reality_tests = json.load(f)
                # Преобразуем строковые ключи пользователей обратно в int
                reality_tests = {int(k): v for k, v in reality_tests.items()}
            log_bot_action(f"Loaded {len(reality_tests)} reality tests from file")
        else:
            reality_tests = {}
    except Exception as e:
        log_bot_action(f"Error loading reality tests: {str(e)}")
        reality_tests = {}

def add_reality_test(user_id: int, ticker: str, target_date: str, 
                    forecast: np.ndarray, forecast_dates: List[str], 
                    amount: int, model_name: str) -> bool:
    """
    Добавить новый тест реальности
    
    Args:
        user_id: ID пользователя
        ticker: Тикер актива
        target_date: Целевая дата для проверки (YYYY-MM-DD)
        forecast: Массив прогнозных значений
        forecast_dates: Список дат прогноза
        amount: Сумма инвестиций
        model_name: Название модели
    """
    print(f"🔧 Вызов add_reality_test для пользователя {user_id}")
    print(f"   📈 Тикер: {ticker}")
    print(f"   📅 Дата: {target_date}")
    print(f"   🤖 Модель: {model_name}")
    print(f"   💰 Сумма: {amount}")
    
    try:
        reality_tests[user_id] = {
            "ticker": ticker,
            "target_date": target_date,
            "forecast": forecast.tolist() if isinstance(forecast, np.ndarray) else forecast,
            "forecast_dates": forecast_dates,
            "amount": amount,
            "model_name": model_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_reality_tests()
        print(f"✅ Тест реальности добавлен для пользователя {user_id}")
        log_bot_action(f"Added reality test for user {user_id}, ticker {ticker}, target date {target_date}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении теста: {str(e)}")
        import traceback
        traceback.print_exc()
        log_bot_action(f"Error adding reality test: {str(e)}")
        return False

def get_user_reality_test(user_id: int) -> Optional[Dict]:
    """Получить активный тест реальности пользователя"""
    return reality_tests.get(user_id)

def remove_reality_test(user_id: int) -> bool:
    """Удалить тест реальности пользователя"""
    try:
        if user_id in reality_tests:
            del reality_tests[user_id]
            save_reality_tests()
            log_bot_action(f"Removed reality test for user {user_id}")
            return True
        return False
    except Exception as e:
        log_bot_action(f"Error removing reality test: {str(e)}")
        return False

def check_ready_tests() -> List[Tuple[int, Dict]]:
    """
    Проверить, какие тесты готовы к выполнению
    Возвращает список кортежей (user_id, test_data) для тестов, чья дата наступила
    """
    ready_tests = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for user_id, test_data in reality_tests.items():
        if test_data["target_date"] <= current_date:
            ready_tests.append((user_id, test_data))
    
    return ready_tests

def calculate_forecast_accuracy(forecast: List[float], actual: List[float]) -> Dict[str, float]:
    """
    Вычислить метрики точности прогноза
    
    Args:
        forecast: Прогнозные значения
        actual: Фактические значения
    
    Returns:
        Словарь с метриками: RMSE, MAPE, MAE, accuracy_percentage
    """
    forecast = np.array(forecast)
    actual = np.array(actual)
    
    # Убедимся, что массивы одинаковой длины
    min_len = min(len(forecast), len(actual))
    forecast = forecast[:min_len]
    actual = actual[:min_len]
    
    if len(forecast) == 0 or len(actual) == 0:
        return {"error": "Empty data for comparison"}
    
    # RMSE (Root Mean Square Error)
    rmse = np.sqrt(np.mean((forecast - actual) ** 2))
    
    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((actual - forecast) / actual)) * 100
    
    # MAE (Mean Absolute Error)
    mae = np.mean(np.abs(forecast - actual))
    
    # Процент точности (в пределах 5% от фактического значения)
    accuracy_5_percent = np.mean(np.abs((forecast - actual) / actual) <= 0.05) * 100
    
    # Процент точности (в пределах 10% от фактического значения)
    accuracy_10_percent = np.mean(np.abs((forecast - actual) / actual) <= 0.10) * 100
    
    # Направленная точность (правильность предсказания направления изменения)
    forecast_direction = np.sign(np.diff(forecast))
    actual_direction = np.sign(np.diff(actual))
    direction_accuracy = np.mean(forecast_direction == actual_direction) * 100 if len(forecast_direction) > 0 else 0
    
    return {
        "rmse": float(rmse),
        "mape": float(mape),
        "mae": float(mae),
        "accuracy_5_percent": float(accuracy_5_percent),
        "accuracy_10_percent": float(accuracy_10_percent),
        "direction_accuracy": float(direction_accuracy),
        "forecast_days": len(forecast),
        "avg_forecast": float(np.mean(forecast)),
        "avg_actual": float(np.mean(actual)),
        "forecast_start": float(forecast[0]),
        "forecast_end": float(forecast[-1]),
        "actual_start": float(actual[0]),
        "actual_end": float(actual[-1])
    }

async def execute_reality_test(user_id: int, test_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
    """
    Выполнить тест реальности
    
    Returns:
        Tuple[успех, сообщение, результаты_метрик]
    """
    try:
        ticker = test_data["ticker"]
        forecast = test_data["forecast"]
        forecast_dates = test_data["forecast_dates"]
        model_name = test_data["model_name"]
        
        log_bot_action(f"Executing reality test for user {user_id}, ticker {ticker}")
        
        # Получаем актуальные данные
        df = get_finance_data(ticker)
        if df is None:
            return False, "❌ Не удалось получить актуальные данные котировок", None
        
        # Находим фактические значения для дат прогноза
        actual_values = []
        available_dates = []
        
        for date_str in forecast_dates:
            try:
                target_date = pd.to_datetime(date_str).date()
                # Ищем ближайшую доступную дату (учитывая выходные)
                for i in range(7):  # Ищем в пределах недели
                    check_date = target_date + timedelta(days=i)
                    matching_rows = df[df.index.date == check_date]
                    if not matching_rows.empty:
                        actual_values.append(float(matching_rows['Close'].iloc[0]))
                        available_dates.append(date_str)
                        break
                else:
                    # Если не найдено точное совпадение, берем ближайшее
                    future_data = df[df.index.date >= target_date]
                    if not future_data.empty:
                        actual_values.append(float(future_data['Close'].iloc[0]))
                        available_dates.append(date_str)
            except Exception as e:
                log_bot_action(f"Error processing date {date_str}: {str(e)}")
                continue
        
        if len(actual_values) == 0:
            return False, "❌ Не удалось найти фактические данные для дат прогноза", None
        
        # Обрезаем прогноз до доступных дат
        available_forecast = forecast[:len(actual_values)]
        
        # Вычисляем метрики
        metrics = calculate_forecast_accuracy(available_forecast, actual_values)
        
        if "error" in metrics:
            return False, f"❌ Ошибка при вычислении метрик: {metrics['error']}", None
        
        # Формируем отчет
        report = f"""
🔬 **ИСПЫТАНИЕ РЕАЛЬНОСТЬЮ ЗАВЕРШЕНО**

📈 **Актив:** {ticker}
🤖 **Модель:** {model_name}
📅 **Период прогноза:** {len(available_forecast)} дней
💰 **Сумма инвестиций:** ${test_data['amount']}

📊 **МЕТРИКИ ТОЧНОСТИ:**
• **RMSE:** {metrics['rmse']:.2f}
• **MAPE:** {metrics['mape']:.2f}%
• **MAE:** {metrics['mae']:.2f}
• **Точность ±5%:** {metrics['accuracy_5_percent']:.1f}%
• **Точность ±10%:** {metrics['accuracy_10_percent']:.1f}%
• **Точность направления:** {metrics['direction_accuracy']:.1f}%

📈 **СРАВНЕНИЕ ЗНАЧЕНИЙ:**
• **Прогноз:** ${metrics['forecast_start']:.2f} → ${metrics['forecast_end']:.2f}
• **Реальность:** ${metrics['actual_start']:.2f} → ${metrics['actual_end']:.2f}
• **Средний прогноз:** ${metrics['avg_forecast']:.2f}
• **Средняя реальность:** ${metrics['avg_actual']:.2f}

💡 **ОЦЕНКА МОДЕЛИ:**
"""
        
        # Добавляем оценку качества
        if metrics['mape'] < 5:
            report += "🟢 **ОТЛИЧНАЯ** точность прогноза!"
        elif metrics['mape'] < 10:
            report += "🟡 **ХОРОШАЯ** точность прогноза"
        elif metrics['mape'] < 20:
            report += "🟠 **СРЕДНЯЯ** точность прогноза"
        else:
            report += "🔴 **НИЗКАЯ** точность прогноза"
        
        if metrics['direction_accuracy'] > 70:
            report += "\n✅ Модель хорошо предсказывает направление движения цены"
        elif metrics['direction_accuracy'] > 50:
            report += "\n⚠️ Модель умеренно предсказывает направление движения цены"
        else:
            report += "\n❌ Модель плохо предсказывает направление движения цены"
        
        # Сохраняем результат в файл
        result_folder = f"RealityTests/{ticker}-{datetime.now().strftime('%Y-%m-%d')}"
        os.makedirs(result_folder, exist_ok=True)
        
        result_data = {
            "test_data": test_data,
            "metrics": metrics,
            "actual_values": actual_values,
            "available_dates": available_dates,
            "report": report,
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        result_file = os.path.join(result_folder, f"reality_test_results.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        log_bot_action(f"Reality test completed for user {user_id}, saved to {result_file}")
        
        return True, report, metrics
        
    except Exception as e:
        error_msg = f"❌ Ошибка при выполнении теста реальности: {str(e)}"
        log_bot_action(f"Error in reality test execution: {str(e)}")
        return False, error_msg, None

def get_all_user_tests() -> Dict[int, Dict]:
    """Получить все активные тесты"""
    return reality_tests.copy()

def get_user_all_tests(user_id: int) -> Dict[str, Dict]:
    """
    Получить все тесты пользователя (старые + новые структурированные)
    
    Returns:
        Dict с ключами как ID тестов и значениями как данные тестов
    """
    user_tests = {}
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Добавляем старый тест из reality_tests.json
    if user_id in reality_tests:
        test_data = reality_tests[user_id].copy()
        test_data["source"] = "old"
        test_data["test_id"] = f"old_{user_id}"
        test_data["status"] = "ready" if test_data["target_date"] <= current_date else "waiting"
        user_tests[f"old_{user_id}"] = test_data
    
    # Добавляем новые структурированные тесты из RealityTests/
    reality_tests_dir = "RealityTests"
    if os.path.exists(reality_tests_dir):
        for test_folder in os.listdir(reality_tests_dir):
            test_folder_path = os.path.join(reality_tests_dir, test_folder)
            if os.path.isdir(test_folder_path):
                test_details_path = os.path.join(test_folder_path, "test_details.json")
                if os.path.exists(test_details_path):
                    try:
                        with open(test_details_path, 'r', encoding='utf-8') as f:
                            test_data = json.load(f)
                        
                        # Проверяем, принадлежит ли тест этому пользователю
                        if test_data.get("user_id") == user_id:
                            test_data["source"] = "new"
                            test_data["folder_path"] = test_folder_path
                            
                            # Определяем статус
                            target_date = test_data.get("target_date", "")
                            has_results = os.path.exists(os.path.join(test_folder_path, "test_results.json"))
                            
                            if has_results:
                                test_data["status"] = "completed"
                            elif target_date <= current_date:
                                test_data["status"] = "ready"
                            else:
                                test_data["status"] = "waiting"
                            
                            user_tests[test_data.get("test_id", test_folder)] = test_data
                    except Exception as e:
                        print(f"❌ Ошибка при чтении теста {test_folder}: {str(e)}")
    
    return user_tests

def format_test_summary(test_data: Dict) -> str:
    """Форматировать краткую сводку теста"""
    ticker = test_data.get("ticker", "Unknown")
    model_name = test_data.get("model_name", "Unknown")
    target_date = test_data.get("target_date", "Unknown")
    amount = test_data.get("amount", 0)
    status = test_data.get("status", "unknown")
    
    # Определяем иконку статуса
    status_icon = {
        "waiting": "⏳",
        "ready": "🔬", 
        "completed": "✅"
    }.get(status, "❓")
    
    # Определяем текст статуса
    status_text = {
        "waiting": "Ожидание даты",
        "ready": "Готов к выполнению", 
        "completed": "Выполнен"
    }.get(status, "Неизвестно")
    
    return f"{status_icon} {ticker} | {model_name} | ${amount} | {target_date} | {status_text}"

def get_test_details(test_id: str, user_id: int) -> Optional[Dict]:
    """Получить детальную информацию о тесте"""
    user_tests = get_user_all_tests(user_id)
    return user_tests.get(test_id)

def delete_user_test(test_id: str, user_id: int) -> bool:
    """Удалить тест пользователя"""
    try:
        user_tests = get_user_all_tests(user_id)
        test_data = user_tests.get(test_id)
        
        if not test_data:
            return False
        
        if test_data.get("source") == "old":
            # Удаляем из старой системы
            return remove_reality_test(user_id)
        else:
            # Удаляем из новой системы
            folder_path = test_data.get("folder_path")
            if folder_path and os.path.exists(folder_path):
                import shutil
                shutil.rmtree(folder_path)
                return True
        
        return False
    except Exception as e:
        print(f"❌ Ошибка при удалении теста {test_id}: {str(e)}")
        return False
def get_reality_tests_statistics():
    """
    Получить статистику по всем тестам реальности
    
    Returns:
        Dict с информацией о тестах: waiting_count, ready_count, completed_count, total_count
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Статистика по старым тестам из reality_tests.json
    waiting_old = 0
    ready_old = 0
    
    for user_id, test_data in reality_tests.items():
        target_date = test_data["target_date"]
        if target_date <= current_date:
            ready_old += 1
        else:
            waiting_old += 1
    
    # Статистика по новым структурированным тестам из RealityTests/
    waiting_new = 0
    ready_new = 0
    completed_new = 0
    
    reality_tests_dir = "RealityTests"
    if os.path.exists(reality_tests_dir):
        for test_folder in os.listdir(reality_tests_dir):
            test_folder_path = os.path.join(reality_tests_dir, test_folder)
            if os.path.isdir(test_folder_path):
                test_details_path = os.path.join(test_folder_path, "test_details.json")
                if os.path.exists(test_details_path):
                    try:
                        with open(test_details_path, 'r', encoding='utf-8') as f:
                            test_data = json.load(f)
                        
                        target_date = test_data.get("target_date", "")
                        has_results = os.path.exists(os.path.join(test_folder_path, "test_results.json"))
                        
                        if has_results:
                            completed_new += 1
                        elif target_date <= current_date:
                            ready_new += 1
                        else:
                            waiting_new += 1
                    except Exception as e:
                        print(f"❌ Ошибка при чтении теста {test_folder}: {str(e)}")
    
    total_waiting = waiting_old + waiting_new
    total_ready = ready_old + ready_new
    total_completed = completed_new  # Старые тесты не имеют функции завершения
    total_count = total_waiting + total_ready + total_completed
    
    return {
        "waiting_count": total_waiting,
        "ready_count": total_ready,
        "completed_count": total_completed,
        "total_count": total_count,
        "old_tests": {"waiting": waiting_old, "ready": ready_old},
        "new_tests": {"waiting": waiting_new, "ready": ready_new, "completed": completed_new}
    }
def format_test_status(test_data: Dict) -> str:
    """Форматировать статус теста для отображения пользователю"""
    target_date = test_data["target_date"]
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    if target_date <= current_date:
        status = "🔬 Готов к выполнению"
    else:
        days_left = (datetime.strptime(target_date, "%Y-%m-%d") - datetime.now()).days
        status = f"⏳ Осталось {days_left} дней"
    
    return f"""
🧪 **АКТИВНЫЙ ТЕСТ РЕАЛЬНОСТИ**
📈 Актив: {test_data['ticker']}
🤖 Модель: {test_data['model_name']}
📅 Целевая дата: {target_date}
💰 Сумма: ${test_data['amount']}
📊 Дней прогноза: {len(test_data['forecast'])}
{status}
"""

def delete_all_user_tests(user_id: int) -> Dict[str, int]:
    """
    Удалить все тесты пользователя
    
    Returns:
        Dict с информацией об удаленных тестах: {"old_tests": count, "new_tests": count, "total": count}
    """
    deleted_count = {"old_tests": 0, "new_tests": 0, "total": 0}
    
    try:
        # Удаляем старые тесты из reality_tests.json
        if user_id in reality_tests:
            del reality_tests[user_id]
            save_reality_tests()
            deleted_count["old_tests"] = 1
            print(f"✅ Удален старый тест пользователя {user_id}")
        
        # Удаляем новые структурированные тесты из RealityTests/
        reality_tests_dir = "RealityTests"
        if os.path.exists(reality_tests_dir):
            folders_to_delete = []
            
            for test_folder in os.listdir(reality_tests_dir):
                test_folder_path = os.path.join(reality_tests_dir, test_folder)
                if os.path.isdir(test_folder_path):
                    test_details_path = os.path.join(test_folder_path, "test_details.json")
                    if os.path.exists(test_details_path):
                        try:
                            with open(test_details_path, 'r', encoding='utf-8') as f:
                                test_data = json.load(f)
                            
                            # Проверяем, принадлежит ли тест этому пользователю
                            if test_data.get("user_id") == user_id:
                                folders_to_delete.append(test_folder_path)
                        except Exception as e:
                            print(f"❌ Ошибка при чтении теста {test_folder}: {str(e)}")
            
            # Удаляем найденные папки
            for folder_path in folders_to_delete:
                try:
                    import shutil
                    shutil.rmtree(folder_path)
                    deleted_count["new_tests"] += 1
                    print(f"✅ Удалена папка теста: {folder_path}")
                except Exception as e:
                    print(f"❌ Ошибка при удалении папки {folder_path}: {str(e)}")
        
        deleted_count["total"] = deleted_count["old_tests"] + deleted_count["new_tests"]
        
        if deleted_count["total"] > 0:
            print(f"✅ Всего удалено тестов пользователя {user_id}: {deleted_count['total']}")
        else:
            print(f"ℹ️ У пользователя {user_id} не найдено тестов для удаления")
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ Ошибка при удалении всех тестов пользователя {user_id}: {str(e)}")
        return {"old_tests": 0, "new_tests": 0, "total": 0}

# Загружаем тесты при импорте модуля
load_reality_tests()