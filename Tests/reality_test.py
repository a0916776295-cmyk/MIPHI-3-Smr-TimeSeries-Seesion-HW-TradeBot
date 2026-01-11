# -*- coding: utf-8 -*-
"""
Модуль для тестирования реальности прогнозов
Позволяет создавать тесты с прогнозами и проверять их точность на реальных данных
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd

# Глобальное хранилище тестов реальности
reality_tests = {}
REALITY_TESTS_FILE = "reality_tests.json"
REALITY_TESTS_DIR = "RealityTests"

def safe_print(text):
    """Безопасный вывод текста с поддержкой кириллицы"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print("Output encoding error")

def load_reality_tests():
    """Загружает тесты реальности из файла"""
    global reality_tests
    try:
        if os.path.exists(REALITY_TESTS_FILE):
            with open(REALITY_TESTS_FILE, 'r', encoding='utf-8') as f:
                reality_tests = json.load(f)
            safe_print(f"📥 Загружено {len(reality_tests)} тестов реальности")
        else:
            reality_tests = {}
            safe_print("📁 Файл тестов реальности не найден, создается новый")
    except json.JSONDecodeError as e:
        safe_print(f"❌ Файл reality_tests.json поврежден: {e}")
        safe_print("🔧 Создается резервная копия и новый файл...")
        # Создаем бэкап поврежденного файла
        import shutil
        try:
            shutil.copy(REALITY_TESTS_FILE, f"{REALITY_TESTS_FILE}.backup")
            safe_print(f"💾 Резервная копия сохранена как {REALITY_TESTS_FILE}.backup")
        except:
            pass
        reality_tests = {}
    except Exception as e:
        safe_print(f"❌ Ошибка загрузки тестов реальности: {e}")
        reality_tests = {}

def save_reality_tests():
    """Сохраняет тесты реальности в файл с защитой от повреждения"""
    try:
        import tempfile
        import os
        
        # Атомарная запись: сначала во временный файл
        temp_file = f"{REALITY_TESTS_FILE}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(reality_tests, f, ensure_ascii=False, indent=2)
        
        # Заменяем основной файл только если запись успешна
        if os.path.exists(temp_file):
            if os.path.exists(REALITY_TESTS_FILE):
                os.replace(temp_file, REALITY_TESTS_FILE)
            else:
                os.rename(temp_file, REALITY_TESTS_FILE)
        
        safe_print(f"💾 Сохранено {len(reality_tests)} тестов реальности")
    except Exception as e:
        safe_print(f"❌ Ошибка сохранения тестов реальности: {e}")
        # Удаляем временный файл если остался
        temp_file = f"{REALITY_TESTS_FILE}.tmp"
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass

def add_reality_test(user_id: int, ticker: str, target_date: str, predictions: List[float], 
                     forecast_dates: List[str], amount: int, model_name: str) -> bool:
    """
    Добавляет новый тест реальности
    
    Args:
        user_id: ID пользователя Telegram
        ticker: Тикер акции
        target_date: Дата для проверки (YYYY-MM-DD)
        predictions: Список прогнозных цен
        forecast_dates: Список дат прогноза
        amount: Сумма инвестиций
        model_name: Название модели
        
    Returns:
        True если тест успешно добавлен
    """
    try:
        load_reality_tests()
        
        # Удаляем существующий тест пользователя если есть
        if str(user_id) in reality_tests:
            safe_print(f"⚠️ Заменяем существующий тест пользователя {user_id}")
        
        # Создаем новый тест
        reality_tests[str(user_id)] = {
            "ticker": ticker,
            "target_date": target_date,
            "forecast": predictions,
            "forecast_dates": forecast_dates,
            "amount": amount,
            "model_name": model_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_reality_tests()
        safe_print(f"✅ Добавлен тест реальности для пользователя {user_id}: {ticker} на {target_date}")
        return True
        
    except Exception as e:
        safe_print(f"❌ Ошибка добавления теста реальности: {e}")
        return False

def get_user_reality_test(user_id: int) -> Optional[Dict]:
    """
    Получает тест реальности пользователя
    
    Args:
        user_id: ID пользователя Telegram
        
    Returns:
        Словарь с данными теста или None
    """
    try:
        load_reality_tests()
        return reality_tests.get(str(user_id))
    except Exception as e:
        safe_print(f"❌ Ошибка получения теста пользователя {user_id}: {e}")
        return None

def remove_reality_test(user_id: int) -> bool:
    """
    Удаляет тест реальности пользователя
    
    Args:
        user_id: ID пользователя Telegram
        
    Returns:
        True если тест успешно удален
    """
    try:
        load_reality_tests()
        if str(user_id) in reality_tests:
            del reality_tests[str(user_id)]
            save_reality_tests()
            safe_print(f"🗑️ Удален тест реальности пользователя {user_id}")
            return True
        return False
    except Exception as e:
        safe_print(f"❌ Ошибка удаления теста пользователя {user_id}: {e}")
        return False

def check_ready_tests() -> List[Tuple[int, Dict]]:
    """
    Проверяет какие тесты готовы к выполнению
    
    Returns:
        Список кортежей (user_id, test_data) для готовых тестов
    """
    try:
        load_reality_tests()
        ready_tests = []
        current_date = datetime.now().date()
        
        for user_id_str, test_data in reality_tests.items():
            try:
                target_date = datetime.strptime(test_data["target_date"], "%Y-%m-%d").date()
                if target_date <= current_date:
                    ready_tests.append((int(user_id_str), test_data))
            except ValueError:
                continue
                
        safe_print(f"🔍 Найдено {len(ready_tests)} готовых тестов")
        return ready_tests
        
    except Exception as e:
        safe_print(f"❌ Ошибка проверки готовых тестов: {e}")
        return []

def execute_reality_test(user_id: int, test_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
    """
    Выполняет тест реальности
    
    Args:
        user_id: ID пользователя
        test_data: Данные теста
        
    Returns:
        Кортеж (success, report, metrics)
    """
    try:
        from finance import get_finance_data
        
        ticker = test_data["ticker"]
        target_date = test_data["target_date"]
        predictions = test_data["forecast"]
        amount = test_data["amount"]
        model_name = test_data["model_name"]
        
        safe_print(f"🧪 Выполняю тест реальности: {ticker} на {target_date}")
        
        # Загружаем реальные данные
        df = get_finance_data(ticker)
        if df is None:
            return False, f"❌ Не удалось загрузить данные для {ticker}", None
        
        # Находим реальную цену на целевую дату
        target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
        
        # Ищем ближайшую дату
        available_dates = df.index
        closest_date = min(available_dates, key=lambda x: abs((x - target_datetime).days))
        
        if abs((closest_date - target_datetime).days) > 7:
            return False, f"❌ Нет данных близко к целевой дате {target_date}", None
        
        real_price = df.loc[closest_date]['Close']
        predicted_price = predictions[-1] if predictions else 0
        
        # Рассчитываем метрики
        error_abs = abs(real_price - predicted_price)
        error_percent = (error_abs / real_price) * 100 if real_price > 0 else 0
        
        # Определяем точность
        if error_percent <= 5:
            accuracy = "🎯 ВЫСОКАЯ"
        elif error_percent <= 10:
            accuracy = "✅ ХОРОШАЯ"
        elif error_percent <= 20:
            accuracy = "⚠️ СРЕДНЯЯ"
        else:
            accuracy = "❌ НИЗКАЯ"
        
        # Создаем отчет
        report = f"""
🧪 **РЕЗУЛЬТАТ ТЕСТА РЕАЛЬНОСТИ**

📈 **Актив:** {ticker}
📅 **Целевая дата:** {target_date}
🤖 **Модель:** {model_name}
💰 **Сумма:** ${amount}

🎯 **СРАВНЕНИЕ:**
• Прогноз: ${predicted_price:.2f}
• Реальность: ${real_price:.2f}
• Ошибка: ${error_abs:.2f} ({error_percent:.2f}%)

📊 **ТОЧНОСТЬ:** {accuracy}

📋 **ДЕТАЛИ:**
• Ближайшая дата: {closest_date.strftime('%Y-%m-%d')}
• Количество прогнозов: {len(predictions)}
• Горизонт прогноза: {len(predictions)} дней

🏆 **ВЫВОД:** {'Модель показала хороший результат' if error_percent <= 10 else 'Модель требует улучшения'}
"""
        
        metrics = {
            "real_price": float(real_price),
            "predicted_price": float(predicted_price),
            "error_abs": float(error_abs),
            "error_percent": float(error_percent),
            "accuracy": accuracy,
            "test_date": target_date,
            "actual_date": closest_date.strftime('%Y-%m-%d')
        }
        
        safe_print(f"✅ Тест выполнен: {ticker}, ошибка {error_percent:.2f}%")
        return True, report, metrics
        
    except Exception as e:
        error_msg = f"❌ Ошибка выполнения теста: {str(e)}"
        safe_print(error_msg)
        return False, error_msg, None

def format_test_status(test_data: Dict) -> str:
    """
    Форматирует статус теста для отображения
    
    Args:
        test_data: Данные теста
        
    Returns:
        Форматированная строка со статусом
    """
    try:
        ticker = test_data.get("ticker", "Unknown")
        target_date = test_data.get("target_date", "Unknown")
        model_name = test_data.get("model_name", "Unknown")
        amount = test_data.get("amount", 0)
        created_at = test_data.get("created_at", "Unknown")
        
        # Определяем статус
        current_date = datetime.now().date()
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
            days_left = (target_date_obj - current_date).days
            
            if days_left > 0:
                status = f"⏳ Ожидание ({days_left} дней)"
            elif days_left == 0:
                status = "🔬 Готов к выполнению"
            else:
                status = "✅ Просрочен, можно выполнить"
        except:
            status = "❓ Неизвестно"
        
        return f"""
📊 **СТАТУС ТЕСТА РЕАЛЬНОСТИ:**

📈 Актив: {ticker}
🤖 Модель: {model_name}
💰 Сумма: ${amount}
📅 Целевая дата: {target_date}
📋 Статус: {status}
🕒 Создан: {created_at}
"""
    except Exception as e:
        return f"❌ Ошибка форматирования статуса: {str(e)}"

def get_reality_tests_statistics() -> Dict[str, Any]:
    """
    Получает статистику всех тестов реальности
    
    Returns:
        Словарь со статистикой
    """
    try:
        # Загружаем старые тесты
        load_reality_tests()
        old_tests = reality_tests
        
        # Загружаем новые структурированные тесты
        new_tests = {}
        if os.path.exists(REALITY_TESTS_DIR):
            for folder_name in os.listdir(REALITY_TESTS_DIR):
                folder_path = os.path.join(REALITY_TESTS_DIR, folder_name)
                if os.path.isdir(folder_path):
                    test_file = os.path.join(folder_path, "test_details.json")
                    if os.path.exists(test_file):
                        try:
                            with open(test_file, 'r', encoding='utf-8') as f:
                                test_data = json.load(f)
                            new_tests[test_data.get("test_id", folder_name)] = test_data
                        except:
                            continue
        
        current_date = datetime.now().date()
        
        # Анализируем старые тесты
        old_waiting = 0
        old_ready = 0
        for test_data in old_tests.values():
            try:
                target_date = datetime.strptime(test_data["target_date"], "%Y-%m-%d").date()
                if target_date > current_date:
                    old_waiting += 1
                else:
                    old_ready += 1
            except:
                continue
        
        # Анализируем новые тесты
        new_waiting = 0
        new_ready = 0
        new_completed = 0
        for test_data in new_tests.values():
            try:
                target_date = datetime.strptime(test_data["target_date"], "%Y-%m-%d").date()
                folder_path = test_data.get("folder", "")
                results_file = os.path.join(folder_path, "test_results.json")
                
                if os.path.exists(results_file):
                    new_completed += 1
                elif target_date <= current_date:
                    new_ready += 1
                else:
                    new_waiting += 1
            except:
                continue
        
        return {
            "total_count": len(old_tests) + len(new_tests),
            "waiting_count": old_waiting + new_waiting,
            "ready_count": old_ready + new_ready,
            "completed_count": new_completed,
            "old_tests": {
                "waiting": old_waiting,
                "ready": old_ready
            },
            "new_tests": {
                "waiting": new_waiting,
                "ready": new_ready,
                "completed": new_completed
            }
        }
        
    except Exception as e:
        safe_print(f"❌ Ошибка получения статистики: {e}")
        return {
            "total_count": 0,
            "waiting_count": 0,
            "ready_count": 0,
            "completed_count": 0,
            "old_tests": {"waiting": 0, "ready": 0},
            "new_tests": {"waiting": 0, "ready": 0, "completed": 0}
        }

def get_user_all_tests(user_id: int) -> Dict[str, Dict]:
    """
    Получает все тесты пользователя (старые и новые)
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Словарь с тестами пользователя {test_id: test_data}
    """
    try:
        all_tests = {}
        
        # Проверяем старые тесты
        load_reality_tests()
        if str(user_id) in reality_tests:
            test_data = reality_tests[str(user_id)]
            test_data["status"] = _get_test_status(test_data)
            all_tests[f"old_{user_id}"] = test_data
        
        # Проверяем новые структурированные тесты
        if os.path.exists(REALITY_TESTS_DIR):
            for folder_name in os.listdir(REALITY_TESTS_DIR):
                folder_path = os.path.join(REALITY_TESTS_DIR, folder_name)
                if os.path.isdir(folder_path):
                    test_file = os.path.join(folder_path, "test_details.json")
                    if os.path.exists(test_file):
                        try:
                            with open(test_file, 'r', encoding='utf-8') as f:
                                test_data = json.load(f)
                            
                            if test_data.get("user_id") == user_id:
                                test_data["status"] = _get_test_status(test_data)
                                test_id = test_data.get("test_id", folder_name)
                                all_tests[test_id] = test_data
                        except:
                            continue
        
        return all_tests
        
    except Exception as e:
        safe_print(f"❌ Ошибка получения тестов пользователя {user_id}: {e}")
        return {}

def _get_test_status(test_data: Dict) -> str:
    """Определяет статус теста"""
    try:
        current_date = datetime.now().date()
        target_date = datetime.strptime(test_data["target_date"], "%Y-%m-%d").date()
        
        # Проверяем, выполнен ли тест
        folder_path = test_data.get("folder", "")
        if folder_path:
            results_file = os.path.join(folder_path, "test_results.json")
            if os.path.exists(results_file):
                return "completed"
        
        # Проверяем готовность
        if target_date <= current_date:
            return "ready"
        else:
            return "waiting"
    except:
        return "unknown"

def format_test_summary(test_data: Dict) -> str:
    """Форматирует краткую информацию о тесте"""
    try:
        ticker = test_data.get("ticker", "Unknown")
        model_name = test_data.get("model_name", "Unknown")
        target_date = test_data.get("target_date", "Unknown")
        status = test_data.get("status", "unknown")
        
        status_icons = {
            "waiting": "⏳",
            "ready": "🔬", 
            "completed": "✅",
            "unknown": "❓"
        }
        
        icon = status_icons.get(status, "❓")
        return f"{icon} {ticker} ({model_name}) - {target_date}"
    except:
        return "❓ Ошибка форматирования"

def get_test_details(test_id: str, user_id: int) -> Optional[Dict]:
    """
    Получает детали конкретного теста
    
    Args:
        test_id: ID теста
        user_id: ID пользователя
        
    Returns:
        Данные теста или None
    """
    try:
        # Проверяем старые тесты
        if test_id == f"old_{user_id}":
            load_reality_tests()
            test_data = reality_tests.get(str(user_id))
            if test_data:
                test_data["status"] = _get_test_status(test_data)
                return test_data
        
        # Проверяем новые тесты
        if os.path.exists(REALITY_TESTS_DIR):
            for folder_name in os.listdir(REALITY_TESTS_DIR):
                folder_path = os.path.join(REALITY_TESTS_DIR, folder_name)
                if os.path.isdir(folder_path):
                    test_file = os.path.join(folder_path, "test_details.json")
                    if os.path.exists(test_file):
                        try:
                            with open(test_file, 'r', encoding='utf-8') as f:
                                test_data = json.load(f)
                            
                            if (test_data.get("test_id") == test_id and 
                                test_data.get("user_id") == user_id):
                                test_data["status"] = _get_test_status(test_data)
                                return test_data
                        except:
                            continue
        
        return None
        
    except Exception as e:
        safe_print(f"❌ Ошибка получения деталей теста {test_id}: {e}")
        return None

def delete_user_test(test_id: str, user_id: int) -> bool:
    """
    Удаляет конкретный тест пользователя
    
    Args:
        test_id: ID теста
        user_id: ID пользователя
        
    Returns:
        True если успешно удален
    """
    try:
        # Удаление старого теста
        if test_id == f"old_{user_id}":
            return remove_reality_test(user_id)
        
        # Удаление нового структурированного теста
        if os.path.exists(REALITY_TESTS_DIR):
            for folder_name in os.listdir(REALITY_TESTS_DIR):
                folder_path = os.path.join(REALITY_TESTS_DIR, folder_name)
                if os.path.isdir(folder_path):
                    test_file = os.path.join(folder_path, "test_details.json")
                    if os.path.exists(test_file):
                        try:
                            with open(test_file, 'r', encoding='utf-8') as f:
                                test_data = json.load(f)
                            
                            if (test_data.get("test_id") == test_id and 
                                test_data.get("user_id") == user_id):
                                # Удаляем папку теста
                                import shutil
                                shutil.rmtree(folder_path)
                                safe_print(f"🗑️ Удален тест {test_id} пользователя {user_id}")
                                return True
                        except:
                            continue
        
        return False
        
    except Exception as e:
        safe_print(f"❌ Ошибка удаления теста {test_id}: {e}")
        return False

def delete_all_user_tests(user_id: int) -> Dict[str, int]:
    """
    Удаляет все тесты пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Словарь с информацией об удалении
    """
    try:
        deleted_info = {
            "total": 0,
            "old_tests": 0,
            "new_tests": 0
        }
        
        # Удаляем старые тесты
        if remove_reality_test(user_id):
            deleted_info["old_tests"] = 1
            deleted_info["total"] += 1
        
        # Удаляем новые структурированные тесты
        if os.path.exists(REALITY_TESTS_DIR):
            folders_to_delete = []
            
            for folder_name in os.listdir(REALITY_TESTS_DIR):
                folder_path = os.path.join(REALITY_TESTS_DIR, folder_name)
                if os.path.isdir(folder_path):
                    test_file = os.path.join(folder_path, "test_details.json")
                    if os.path.exists(test_file):
                        try:
                            with open(test_file, 'r', encoding='utf-8') as f:
                                test_data = json.load(f)
                            
                            if test_data.get("user_id") == user_id:
                                folders_to_delete.append(folder_path)
                        except:
                            continue
            
            # Удаляем найденные папки
            import shutil
            for folder_path in folders_to_delete:
                try:
                    shutil.rmtree(folder_path)
                    deleted_info["new_tests"] += 1
                    deleted_info["total"] += 1
                except:
                    continue
        
        safe_print(f"🗑️ Удалено {deleted_info['total']} тестов пользователя {user_id}")
        return deleted_info
        
    except Exception as e:
        safe_print(f"❌ Ошибка массового удаления тестов пользователя {user_id}: {e}")
        return {"total": 0, "old_tests": 0, "new_tests": 0}

# Инициализация при импорте
if not os.path.exists(REALITY_TESTS_DIR):
    os.makedirs(REALITY_TESTS_DIR, exist_ok=True)

# Автозагрузка при импорте модуля
load_reality_tests()