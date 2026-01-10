# -*- coding: utf-8 -*-
import asyncio
import pandas as pd
import sys
import os
import json
import uuid
from datetime import timedelta, datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

# Настройка кодировки для Windows
if sys.platform.startswith('win'):
    # Устанавливаем UTF-8 для stdout и stderr
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    # Для старых версий Python можно использовать:
    # import codecs
    # sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    # sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
from config_bot import BOT_TOKEN
from finance import get_finance_data
from graph import generate_graph, generate_forecast_graph, generate_forecast_graph_zoomed
from LoggerModule import log_user_action, log_bot_action
from MenuBot import (
    get_main_menu, get_ticker_menu, get_amount_menu, get_forecast_menu,
    get_help_text, get_about_text, get_status_message, POPULAR_TICKERS,
    get_reality_test_menu, get_test_date_menu, get_reality_test_help_text
)
from Tests.reality_test import (
    add_reality_test, get_user_reality_test, remove_reality_test,
    check_ready_tests, execute_reality_test, format_test_status,
    get_reality_tests_statistics, get_user_all_tests, format_test_summary,
    get_test_details, delete_user_test, delete_all_user_tests
)
from Models.model_comparison import compare_all_models
from trading_recommendations import (
    calculate_trading_strategy, 
    generate_recommendations_text,
    save_recommendations_to_file
)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище состояний пользователей {user_id: {"ticker": str, "amount": int, "forecast_days": int, "mode": str, "temp_forecast": dict}}
user_states = {}

# Файл для сохранения состояний пользователей
USER_STATES_FILE = "user_states.json"

def save_user_states():
    """Сохранить состояния пользователей в файл"""
    try:
        # Конвертируем numpy типы перед сохранением
        serializable_states = convert_numpy_types(user_states)
        with open(USER_STATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_states, f, ensure_ascii=False, indent=2)
        safe_print(f"💾 [{datetime.now().strftime('%H:%M:%S')}] Состояния пользователей сохранены")
    except Exception as e:
        safe_print(f"❌ Ошибка сохранения состояний: {e}")
        import traceback
        safe_print(f"Детали ошибки сохранения: {traceback.format_exc()}")

def load_user_states():
    """Загрузить состояния пользователей из файла"""
    global user_states
    try:
        if os.path.exists(USER_STATES_FILE):
            with open(USER_STATES_FILE, 'r', encoding='utf-8') as f:
                user_states = json.load(f)
            safe_print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Состояния пользователей загружены: {len(user_states)} пользователей")
        else:
            safe_print(f"📁 [{datetime.now().strftime('%H:%M:%S')}] Файл состояний не найден, создаем новый")
    except Exception as e:
        safe_print(f"❌ Ошибка загрузки состояний: {e}")
        user_states = {}

def safe_print(text):
    """Безопасный вывод текста с поддержкой кириллицы"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Попробуем вывести в безопасном формате
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print("Output encoding error")

def get_user_state(user_id):
    """Получить состояние пользователя"""
    if user_id not in user_states:
        user_states[user_id] = {"ticker": None, "amount": None, "forecast_days": 30, "mode": "normal", "temp_forecast": None}
        save_user_states()  # Сохраняем при создании нового пользователя
    return user_states[user_id]

def update_user_state(user_id, **kwargs):
    """Обновить состояние пользователя с автосохранением"""
    state = get_user_state(user_id)
    state.update(kwargs)
    save_user_states()  # Автоматическое сохранение при обновлении

async def format_user_statistics():
    """Форматировать статистику тестов реальности для отправки пользователю"""
    try:
        stats = get_reality_tests_statistics()
        
        statistics_text = (
            "📈 **СТАТИСТИКА ТЕСТОВ РЕАЛЬНОСТИ:**\n\n"
            f"🔬 Всего тестов: **{stats['total_count']}**\n"
            f"⏳ Ожидают наступления даты: **{stats['waiting_count']}**\n"
            f"🔬 Готовы к выполнению: **{stats['ready_count']}**\n"
            f"✅ Уже выполнены: **{stats['completed_count']}**"
        )
        
        # Добавляем детализацию если есть тесты
        if stats['total_count'] > 0:
            details = []
            if stats['old_tests']['waiting'] > 0 or stats['old_tests']['ready'] > 0:
                details.append(f"📜 Старые тесты: ожидают {stats['old_tests']['waiting']}, готовы {stats['old_tests']['ready']}")
            
            if stats['new_tests']['waiting'] > 0 or stats['new_tests']['ready'] > 0 or stats['new_tests']['completed'] > 0:
                details.append(f"🆕 Новые тесты: ожидают {stats['new_tests']['waiting']}, готовы {stats['new_tests']['ready']}, выполнены {stats['new_tests']['completed']}")
            
            if details:
                statistics_text += "\n\n" + "\n".join(details)
        
        return statistics_text
    except Exception as e:
        safe_print(f"❌ Ошибка при получении статистики: {str(e)}")
        return "❌ Не удалось загрузить статистику тестов реальности"

async def show_user_tests_menu(message: types.Message):
    """Показать меню с тестами пользователя"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    try:
        user_tests = get_user_all_tests(user_id)
        
        if not user_tests:
            await message.answer(
                "🧪 **МОИ ТЕСТЫ РЕАЛЬНОСТИ**\n\n"
                "У вас пока нет активных тестов реальности.\n\n"
                "📝 Чтобы создать тест:\n"
                "1. Получите прогноз для любого актива\n"
                "2. Нажмите 'Да, создать тест' когда система предложит\n"
                "3. Выберите дату для проверки\n\n"
                "🎯 Тесты реальности помогают оценить точность моделей прогнозирования!",
                reply_markup=get_main_menu()
            )
            return
        
        # Создаем клавиатуру со списком тестов
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        keyboard_buttons = []
        menu_text = "🧪 **МОИ ТЕСТЫ РЕАЛЬНОСТИ**\n\n"
        
        test_counter = 1
        for test_id, test_data in user_tests.items():
            # Добавляем краткую информацию о тесте
            test_summary = format_test_summary(test_data)
            menu_text += f"{test_counter}. {test_summary}\n"
            
            # Создаем кнопку с информацией о статусе
            ticker = test_data.get('ticker', 'Unknown')
            status = test_data.get('status', 'unknown')
            
            # Определяем иконку и текст статуса для кнопки
            if status == "waiting":
                status_icon = "⏳"
                status_text = "Ожидает"
            elif status == "ready":
                status_icon = "🔬"
                status_text = "Готов"
            elif status == "completed":
                status_icon = "✅"
                status_text = "Выполнен"
            else:
                status_icon = "❓"
                status_text = "Неизвестно"
            
            button_text = f"{status_icon} {ticker} - {status_text}"
            keyboard_buttons.append([KeyboardButton(text=button_text)])
            test_counter += 1
        
        # Добавляем служебные кнопки
        keyboard_buttons.extend([
            [KeyboardButton(text="📈 Общая статистика")],
            [KeyboardButton(text="�️ Удалить все тесты")],
            [KeyboardButton(text="�🔙 Главное меню")]
        ])
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=keyboard_buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        menu_text += (
            f"\n📊 **Итого:** {len(user_tests)} тестов\n\n"
            "💡 Нажмите на любой тест для просмотра деталей.\n"
            "📋 **Статусы:**\n"
            "⏳ Ожидает - тест ждет наступления целевой даты\n"
            "🔬 Готов - тест можно выполнить прямо сейчас\n"
            "✅ Выполнен - результаты готовы к просмотру"
        )
        
        update_user_state(user_id, mode="viewing_tests", user_tests_list=list(user_tests.keys()))
        
        await message.answer(menu_text, reply_markup=keyboard, parse_mode="Markdown")
        
        safe_print(f"📋 [{datetime.now().strftime('%H:%M:%S')}] Показан список тестов пользователю {username}: {len(user_tests)} тестов")
        
    except Exception as e:
        safe_print(f"❌ Ошибка при показе тестов пользователю {username}: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при загрузке ваших тестов.\n"
            "Попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_menu()
        )

async def show_test_details(message: types.Message, test_number: int):
    """Показать детали конкретного теста"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    state = get_user_state(user_id)
    
    try:
        tests_list = state.get("user_tests_list", [])
        if test_number < 1 or test_number > len(tests_list):
            await message.answer("❌ Неверный номер теста")
            return
        
        test_id = tests_list[test_number - 1]
        test_data = get_test_details(test_id, user_id)
        
        if not test_data:
            await message.answer("❌ Тест не найден")
            return
        
        # Формируем детальную информацию
        current_date = datetime.now().strftime("%Y-%m-%d")
        target_date = test_data.get("target_date", "")
        status = test_data.get("status", "unknown")
        
        status_map = {'waiting': '⏳ Ожидание даты', 'ready': '🔬 Готов к выполнению', 'completed': '✅ Выполнен'}
        status_text = status_map.get(status, '❓ Неизвестно')
        
        details_text = f"""
🔬 **ДЕТАЛИ ТЕСТА #{test_number}**

📈 **Актив:** {test_data.get('ticker', 'Unknown')}
🤖 **Модель:** {test_data.get('model_name', 'Unknown')}
💰 **Сумма:** ${test_data.get('amount', 0)}
📅 **Целевая дата:** {target_date}
📊 **Дней прогноза:** {len(test_data.get('predictions', test_data.get('forecast', [])))}
🗓️ **Создан:** {test_data.get('created_at', 'Неизвестно')}

📋 **Статус:** {status_text}
"""
        
        # Добавляем дополнительную информацию в зависимости от статуса
        if status == "waiting":
            try:
                days_left = (datetime.strptime(target_date, "%Y-%m-%d") - datetime.now()).days
                details_text += f"⏰ **Осталось дней:** {days_left}\n"
            except:
                pass
        elif status == "completed":
            details_text += "\n🎉 **Тест выполнен!** Результаты доступны для просмотра.\n"
        
        # Показываем прогнозные данные (первые и последние значения)
        predictions = test_data.get('predictions', test_data.get('forecast', []))
        if predictions and len(predictions) > 0:
            details_text += f"\n📈 **Прогноз:** ${predictions[0]:.2f}"
            if len(predictions) > 1:
                details_text += f" → ${predictions[-1]:.2f}"
        
        # Добавляем информацию о торговой стратегии
        trading_recs = test_data.get('trading_recommendations', [])
        expected_profit = test_data.get('expected_profit', 0)
        profit_percent = test_data.get('profit_percent', 0)
        
        if trading_recs or expected_profit != 0:
            details_text += f"\n\n💼 **ТОРГОВАЯ СТРАТЕГИЯ:**\n"
            
            if expected_profit != 0:
                details_text += f"💵 **Ожидаемая прибыль:** ${expected_profit:.2f}\n"
                details_text += f"📊 **Доходность:** {profit_percent:+.2f}%\n"
                
                if profit_percent > 10:
                    details_text += "🚀 **Высокодоходная стратегия**\n"
                elif profit_percent > 5:
                    details_text += "✅ **Прибыльная стратегия**\n"
                elif profit_percent > 0:
                    details_text += "📈 **Умеренная прибыль**\n"
                else:
                    details_text += "⚠️ **Потенциальные убытки**\n"
            
            # Показываем рекомендации (первые 2-3)
            if trading_recs and len(trading_recs) > 0:
                details_text += f"\n🎯 **Рекомендации ({len(trading_recs)} всего):**\n"
                for i, rec in enumerate(trading_recs[:3]):  # Показываем первые 3
                    if isinstance(rec, dict):
                        action = rec.get('action', 'N/A')
                        price = rec.get('price', 0)
                        date = rec.get('date', 'N/A')
                        expected_profit = rec.get('expected_profit', 0)
                        
                        # Обрабатываем разные форматы цены (новый числовой и старый строковый)
                        if isinstance(price, str) and price.startswith('$'):
                            price_value = float(price[1:])
                        elif isinstance(price, (int, float)):
                            price_value = float(price)
                        else:
                            price_value = 0
                        
                        profit_text = f" (ожид. прибыль: ${expected_profit:.2f})" if expected_profit != 0 else ""
                        details_text += f"• {date} - {action} по ${price_value:.2f}{profit_text}\n"
                
                if len(trading_recs) > 3:
                    details_text += f"• ... и еще {len(trading_recs) - 3} рекомендаций\n"
        
        # Создаем клавиатуру с действиями
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        action_buttons = []
        
        if status == "ready":
            action_buttons.append([KeyboardButton(text=f"▶️ Выполнить тест #{test_number}")])
        elif status == "completed":
            action_buttons.append([KeyboardButton(text=f"📊 Результаты #{test_number}")])
        
        if status == "waiting":
            action_buttons.append([KeyboardButton(text=f"ℹ️ Инфо об ожидании #{test_number}")])
        
        # Добавляем кнопку торговой стратегии если есть рекомендации
        if trading_recs or expected_profit != 0:
            action_buttons.append([KeyboardButton(text=f"💼 Торговая стратегия #{test_number}")])
        
        action_buttons.extend([
            [KeyboardButton(text=f"🗑️ Удалить тест #{test_number}")],
            [KeyboardButton(text="🔙 К списку тестов")],
            [KeyboardButton(text="🏠 Главное меню")]
        ])
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=action_buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        update_user_state(user_id, mode="test_details", selected_test_id=test_id, selected_test_number=test_number)
        
        await message.answer(details_text, reply_markup=keyboard, parse_mode="Markdown")
        
        safe_print(f"📋 [{datetime.now().strftime('%H:%M:%S')}] Показаны детали теста #{test_number} пользователю {username}")
        
    except Exception as e:
        safe_print(f"❌ Ошибка при показе деталей теста пользователю {username}: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при загрузке деталей теста.",
            reply_markup=get_main_menu()
        )

def convert_numpy_types(obj):
    """
    Рекурсивно преобразует numpy типы данных в обычные Python типы для JSON сериализации
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif hasattr(obj, 'item'):  # numpy скаляр
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy массив
        return obj.tolist()
    else:
        return obj

async def create_structured_reality_test(user_id, username, forecast_data, target_date, message):
    """Создает структурированный тест реальности с сохранением в отдельную папку"""
    try:
        safe_print(f"🔧 [{datetime.now().strftime('%H:%M:%S')}] НАЧАЛО create_structured_reality_test")
        safe_print(f"   👤 User: {user_id} ({username})")
        safe_print(f"   📅 Target Date: {target_date}")
        safe_print(f"   📊 Forecast Data Keys: {list(forecast_data.keys()) if forecast_data else 'НЕТ ДАННЫХ!'}")
        
        if not forecast_data:
            safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] forecast_data пуст!")
            return {"success": False, "error": "Данные прогноза отсутствуют"}
        
        # Генерируем уникальный ID теста
        test_id = str(uuid.uuid4())[:8]
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создаем папку для теста
        test_folder = f"RealityTests/{forecast_data['ticker']}_test_{current_time}_{test_id}"
        os.makedirs(test_folder, exist_ok=True)
        
        safe_print(f"📁 [{datetime.now().strftime('%H:%M:%S')}] Создана папка теста: {test_folder}")
        
        # Генерируем даты прогноза
        import pandas as pd
        forecast_dates = pd.date_range(
            start=datetime.now().date(),
            periods=len(forecast_data["predictions"]),
            freq='D'
        ).strftime('%Y-%m-%d').tolist()
        
        # Подготавливаем данные теста
        test_data = {
            "test_id": test_id,
            "user_id": user_id,
            "username": username,
            "ticker": forecast_data['ticker'],
            "target_date": target_date,
            "predictions": forecast_data['predictions'].tolist() if hasattr(forecast_data['predictions'], 'tolist') else forecast_data['predictions'],
            "forecast_dates": forecast_dates,
            "amount": forecast_data['amount'],
            "model_name": forecast_data['model_name'],
            "trading_recommendations": convert_numpy_types(forecast_data.get('trading_recommendations', [])),
            "expected_profit": forecast_data.get('expected_profit', 0),
            "profit_percent": forecast_data.get('profit_percent', 0),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "folder": test_folder,
            "forecast_days": len(forecast_data['predictions'])
        }
        
        # Сохраняем детали теста в JSON
        test_file = os.path.join(test_folder, "test_details.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Сохраняем прогноз отдельно
        forecast_file = os.path.join(test_folder, "forecast_data.json")
        with open(forecast_file, 'w', encoding='utf-8') as f:
            json.dump({
                "predictions": test_data["predictions"],
                "dates": forecast_dates,
                "model": forecast_data['model_name'],
                "ticker": forecast_data['ticker']
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем торговую стратегию отдельно
        if forecast_data.get('trading_recommendations'):
            trading_file = os.path.join(test_folder, "trading_strategy.json")
            with open(trading_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "recommendations": convert_numpy_types(forecast_data['trading_recommendations']),
                    "expected_profit": convert_numpy_types(forecast_data.get('expected_profit', 0)),
                    "profit_percent": convert_numpy_types(forecast_data.get('profit_percent', 0)),
                    "investment_amount": convert_numpy_types(forecast_data['amount']),
                    "ticker": forecast_data['ticker'],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, f, ensure_ascii=False, indent=2)
        
        # Добавляем в систему тестов реальности
        success = add_reality_test(
            user_id, 
            forecast_data["ticker"],
            target_date,
            forecast_data["predictions"],
            forecast_dates,
            forecast_data["amount"],
            forecast_data["model_name"]
        )
        
        if success:
            safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Тест {test_id} создан для {username}")
            log_bot_action(f"Created structured reality test {test_id} for user {user_id}")
            
            return {
                "success": True,
                "test_id": test_id,
                "folder": test_folder,
                "target_date": target_date
            }
        else:
            safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка создания теста {test_id} - add_reality_test вернул False")
            safe_print(f"❌ Параметры add_reality_test:")
            safe_print(f"   user_id: {user_id}")
            safe_print(f"   ticker: {forecast_data.get('ticker', 'НЕТ!')}")
            safe_print(f"   target_date: {target_date}")
            safe_print(f"   predictions type: {type(forecast_data.get('predictions', 'НЕТ!'))}")
            safe_print(f"   amount: {forecast_data.get('amount', 'НЕТ!')}")
            safe_print(f"   model_name: {forecast_data.get('model_name', 'НЕТ!')}")
            return {"success": False, "error": "Failed to add to reality test system"}
            
    except Exception as e:
        safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка создания структурированного теста: {str(e)}")
        safe_print(f"❌ Тип ошибки: {type(e).__name__}")
        safe_print(f"❌ User ID: {user_id}, Username: {username}")
        safe_print(f"❌ Target Date: {target_date}")
        safe_print(f"❌ Forecast Data Type: {type(forecast_data)}")
        safe_print(f"❌ Forecast Data Keys: {list(forecast_data.keys()) if forecast_data and isinstance(forecast_data, dict) else 'НЕ СЛОВАРЬ'}")
        import traceback
        safe_print(f"❌ Детали ошибки: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

def get_user_test_status(user_id):
    """Получает статус всех тестов пользователя"""
    try:
        tests = []
        reality_tests_folder = "RealityTests"
        
        if not os.path.exists(reality_tests_folder):
            return tests
        
        # Проходим по всем папкам тестов
        for folder_name in os.listdir(reality_tests_folder):
            folder_path = os.path.join(reality_tests_folder, folder_name)
            if os.path.isdir(folder_path):
                test_file = os.path.join(folder_path, "test_details.json")
                if os.path.exists(test_file):
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            test_data = json.load(f)
                        
                        if test_data.get("user_id") == user_id:
                            # Определяем текущий статус
                            target_date = datetime.strptime(test_data["target_date"], "%Y-%m-%d")
                            current_date = datetime.now()
                            
                            if target_date.date() <= current_date.date():
                                # Проверяем, выполнен ли тест
                                results_file = os.path.join(folder_path, "test_results.json")
                                if os.path.exists(results_file):
                                    test_data["status"] = "completed"
                                else:
                                    test_data["status"] = "ready"
                            else:
                                test_data["status"] = "pending"
                            
                            tests.append(test_data)
                    except Exception as e:
                        safe_print(f"Ошибка чтения теста {folder_name}: {str(e)}")
                        continue
        
        return sorted(tests, key=lambda x: x["created_at"], reverse=True)
        
    except Exception as e:
        safe_print(f"Ошибка получения статуса тестов: {str(e)}")
        return []

async def show_user_tests(message, user_id):
    """Показывает все тесты пользователя с их статусами"""
    tests = get_user_test_status(user_id)
    
    if not tests:
        await message.answer("🔍 У вас пока нет созданных тестов реальности")
        return
    
    response = "🔍 **ВАШИ ТЕСТЫ РЕАЛЬНОСТИ:**\n\n"
    
    for i, test in enumerate(tests, 1):
        status_emoji = {
            "pending": "⏳",
            "ready": "✅",
            "completed": "🏆"
        }.get(test["status"], "❓")
        
        status_text = {
            "pending": "Ожидает даты",
            "ready": "Готов к выполнению",
            "completed": "Завершен"
        }.get(test["status"], "Неизвестно")
        
        response += (
            f"{status_emoji} **Тест #{i}** (ID: {test['test_id']})\n"
            f"   📈 Актив: {test['ticker']}\n"
            f"   🤖 Модель: {test['model_name']}\n"
            f"   📅 Целевая дата: {test['target_date']}\n"
            f"   📊 Статус: {status_text}\n"
            f"   📁 Создан: {test['created_at']}\n\n"
        )
    
    if len(response) > 4000:
        # Разбиваем на части, если слишком длинный
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for part in parts:
            await message.answer(part, parse_mode="Markdown")
    else:
        await message.answer(response, parse_mode="Markdown")

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    safe_print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] Пользователь {username} (ID: {user_id}) запустил бота")
    
    log_user_action(user_id, "Command /start")
    log_bot_action("Sent greeting to user")
    state = get_user_state(user_id)
    keyboard = get_main_menu()
    status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
    
    # Получаем статистику тестов реальности
    statistics = await format_user_statistics()
    
    greeting_message = (
        f"Привет! Я помогу тебе получить графики акций.\n\n"
        f"{status}\n\n"
        f"{statistics}"
    )
    
    await message.answer(
        greeting_message,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Отправлено приветствие со статистикой пользователю {username}")

@dp.message(Command("debug"))
async def debug_info(message: types.Message):
    """Команда для диагностики проблем"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    safe_print(f"🔧 [{datetime.now().strftime('%H:%M:%S')}] Пользователь {username} запустил диагностику")
    
    log_user_action(user_id, "Command /debug")
    
    try:
        # Тестируем загрузку данных для популярного тикера
        await message.answer("🔍 Диагностика системы...")
        safe_print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] Запуск диагностики системы")
        
        from finance import get_finance_data
        test_ticker = "AAPL"
        
        await message.answer(f"📊 Тестирую загрузку данных для {test_ticker}...")
        safe_print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Тестирование загрузки данных для {test_ticker}")
        
        df = get_finance_data(test_ticker)
        
        if df is not None:
            result = (
                f"✅ **Система работает нормально**\n\n"
                f"🔍 Тестовый тикер: {test_ticker}\n"
                f"📊 Записей: {len(df)}\n"
                f"📅 Период: {df.index[0].date()} - {df.index[-1].date()}\n"
                f"💰 Последняя цена: ${df['Close'].iloc[-1]:.2f}\n\n"
                f"💡 Если у вас проблемы с конкретным тикером, попробуйте:\n"
                f"• Другой тикер из списка\n"
                f"• Проверить правильность написания\n"
                f"• Повторить попытку через минуту"
            )
            safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Диагностика успешна - система работает")
        else:
            result = (
                f"❌ **Обнаружены проблемы**\n\n"
                f"Не удалось загрузить данные для {test_ticker}\n\n"
                f"🔧 Возможные решения:\n"
                f"• Проверьте интернет соединение\n"
                f"• Попробуйте позже (может быть перегрузка сервера)\n"
                f"• Обратитесь к администратору"
            )
            safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Диагностика обнаружила проблемы")
        
        await message.answer(result)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка диагностики: {str(e)}")
        safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка диагностики: {str(e)}")
        log_bot_action(f"Debug error: {str(e)}")

@dp.message(Command("restart"))
async def restart_command(message: types.Message):
    """Команда для перезапуска бота"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    safe_print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Пользователь {username} использовал команду /restart")
    
    log_user_action(user_id, "Command /restart")
    state = get_user_state(user_id)
    
    # Очищаем состояние пользователя
    old_state = state.copy()
    state.clear()
    state.update({"ticker": None, "amount": None, "forecast_days": 30, "mode": "normal", "temp_forecast": None})
    
    # Логируем что было сброшено
    if old_state.get("ticker") or old_state.get("amount") or old_state.get("temp_forecast"):
        safe_print(f"🧹 [{datetime.now().strftime('%H:%M:%S')}] Сброшены настройки {username} через команду")
    
    keyboard = get_main_menu()
    status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
    
    await message.answer(
        f"🔄 **БОТ ПЕРЕЗАПУЩЕН**\n\n"
        f"✅ Все настройки сброшены до начальных значений\n"
        f"✅ Система готова к работе\n\n"
        f"{status}",
        reply_markup=keyboard
    )
    
    safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Перезапуск через команду завершен для {username}")

@dp.message()
async def process_message(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    text = message.text or "[медиафайл]"
    
    # Логируем входящее сообщение
    safe_print(f"📨 [{datetime.now().strftime('%H:%M:%S')}] {username} (ID: {user_id}): {text}")
    
    # Проверка работоспособности бота
    if text == "/ping":
        await message.answer("🏓 Pong! Бот работает отлично!")
        safe_print(f"🏓 [{datetime.now().strftime('%H:%M:%S')}] Ping-pong для {username}")
        return
        
    # Диагностика состояния пользователя
    if text == "/status":
        temp_forecast = state.get("temp_forecast")
        status_info = f"🔍 **ДИАГНОСТИКА СОСТОЯНИЯ:**\n\n"
        status_info += f"👤 Пользователь: {username} (ID: {user_id})\n"
        status_info += f"🎛️ Режим: {state.get('mode', 'normal')}\n"
        status_info += f"📊 Тикер: {state.get('ticker', 'не выбрано')}\n"
        status_info += f"💰 Сумма: ${state.get('amount', 'не выбрано')}\n"
        status_info += f"📅 Горизонт: {state.get('forecast_days', 30)} дней\n\n"
        
        if temp_forecast:
            status_info += f"✅ **ПРОГНОЗ НАЙДЕН:**\n"
            status_info += f"📈 Актив: {temp_forecast.get('ticker')}\n"
            status_info += f"🤖 Модель: {temp_forecast.get('model_name')}\n"
            status_info += f"💵 Сумма: ${temp_forecast.get('amount')}\n"
            status_info += f"📊 Прогнозов: {len(temp_forecast.get('predictions', []))}\n"
            status_info += f"🕒 Создан: {temp_forecast.get('created_at')}\n\n"
            status_info += f"🧪 **Можно создать тест реальности!**"
        else:
            status_info += f"❌ **ПРОГНОЗ НЕ НАЙДЕН**\n"
            status_info += f"Temp_forecast = {temp_forecast}\n\n"
            status_info += f"🚫 **Тест реальности недоступен!**"
            
        await message.answer(status_info)
        return
        
    # Автоматическое тестирование механизма реальности
    if text == "/test_reality":
        safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] {username} запускает автотест механизма реальности")
        
        await message.answer("🤖 **АВТОТЕСТ МЕХАНИЗМА РЕАЛЬНОСТИ**\n\nЗапускаю полный цикл тестирования...")
        
        try:
            # 1. Устанавливаем тестовые параметры
            state["ticker"] = "AAPL"
            state["amount"] = 1000
            state["forecast_days"] = 5
            await message.answer("✅ Шаг 1: Настройки установлены (AAPL, $1000, 5 дней)")
            
            # 2. Создаем симулированный прогноз
            import numpy as np
            test_predictions = [150.0, 151.5, 149.8, 152.2, 150.9]  # Симуляция прогноза
            
            state["temp_forecast"] = {
                "ticker": "AAPL",
                "amount": 1000,
                "model_name": "TEST_MODEL",
                "predictions": test_predictions,
                "forecast_days": 5,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            await message.answer("✅ Шаг 2: Тестовый прогноз создан")
            
            # 3. Создаем тест реальности на завтра
            from datetime import timedelta
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            import pandas as pd
            forecast_dates = pd.date_range(
                start=datetime.now().date(),
                periods=5,
                freq='D'
            ).strftime('%Y-%m-%d').tolist()
            
            from Tests.reality_test import add_reality_test
            success = add_reality_test(
                user_id,
                "AAPL", 
                tomorrow,
                test_predictions,
                forecast_dates,
                1000,
                "TEST_MODEL"
            )
            
            if success:
                await message.answer(f"✅ Шаг 3: Тест реальности создан на {tomorrow}")
                
                # 4. Проверяем, что тест сохранился
                from Tests.reality_test import get_user_reality_test
                saved_test = get_user_reality_test(user_id)
                if saved_test:
                    await message.answer("✅ Шаг 4: Тест найден в базе данных")
                    test_info = (
                        f"📊 **СОЗДАННЫЙ ТЕСТ:**\n"
                        f"• Тикер: {saved_test['ticker']}\n"
                        f"• Дата: {saved_test['target_date']}\n"
                        f"• Модель: {saved_test['model_name']}\n"
                        f"• Сумма: ${saved_test['amount']}\n"
                        f"• Прогнозов: {len(saved_test['forecast'])}"
                    )
                    await message.answer(test_info)
                    
                    # 5. Симулируем выполнение теста (меняем дату на сегодня)
                    await message.answer("⏳ Шаг 5: Симулируем выполнение теста...")
                    
                    # Меняем дату теста на сегодня для немедленного выполнения
                    from Tests.reality_test import reality_tests
                    if user_id in reality_tests:
                        reality_tests[user_id]["target_date"] = datetime.now().strftime("%Y-%m-%d")
                        
                        # Проверяем готовые тесты
                        from Tests.reality_test import check_ready_tests, execute_reality_test
                        ready_tests = check_ready_tests()
                        
                        user_ready = [(uid, test) for uid, test in ready_tests if uid == user_id]
                        if user_ready:
                            await message.answer("✅ Тест готов к выполнению!")
                            
                            # Выполняем тест
                            uid, test = user_ready[0]
                            result = execute_reality_test(uid, test)
                            
                            if result and "success" in result:
                                await message.answer("✅ Шаг 6: Тест выполнен успешно!")
                                await message.answer(f"📊 Результат:\n{result['report'][:500]}...")
                                
                                await message.answer(
                                    "🎉 **АВТОТЕСТ ЗАВЕРШЕН УСПЕШНО!**\n\n"
                                    "✅ Все этапы пройдены:\n"
                                    "1. Настройка параметров\n"
                                    "2. Создание прогноза\n" 
                                    "3. Создание теста реальности\n"
                                    "4. Сохранение в базе\n"
                                    "5. Выполнение теста\n"
                                    "6. Генерация отчета\n\n"
                                    "🧪 Механизм работает корректно!"
                                )
                            else:
                                await message.answer("❌ Ошибка при выполнении теста")
                        else:
                            await message.answer("⚠️ Тест не готов к выполнению")
                else:
                    await message.answer("❌ Шаг 4: Тест не найден в базе данных")
            else:
                await message.answer("❌ Ошибка создания теста реальности")
                
        except Exception as e:
            error_msg = str(e)
            await message.answer(f"❌ **ОШИБКА АВТОТЕСТА:**\n{error_msg}")
            safe_print(f"❌ Ошибка в автотесте: {error_msg}")
            import traceback
            safe_print(f"Детали: {traceback.format_exc()}")
        
        return
    
    log_user_action(user_id, text)
    state = get_user_state(user_id)
    
    # Детальное логирование состояния
    safe_print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] Состояние {username}: mode='{state.get('mode')}', temp_forecast={'есть' if state.get('temp_forecast') else 'нет'}")
    safe_print(f"📝 [{datetime.now().strftime('%H:%M:%S')}] Текст сообщения: '{text}'")
    safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] Проверяем режимы обработки для {username}...")
    
    # Проверка на None
    if not message.text:
        safe_print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Получено сообщение без текста от {username}")
        return
    
    # Кнопка "Тикер"
    if message.text == "🔍 Тикер":
        safe_print(f"🎯 [{datetime.now().strftime('%H:%M:%S')}] {username} открыл меню выбора тикера")
        keyboard = get_ticker_menu()
        await message.answer("Выбери тикер акции:", reply_markup=keyboard)
        return
    
    # Кнопка "Сумма"
    if message.text == "💵 Сумма":
        safe_print(f"💰 [{datetime.now().strftime('%H:%M:%S')}] {username} открыл меню выбора суммы")
        keyboard = get_amount_menu()
        await message.answer("Выбери сумму инвестиций:", reply_markup=keyboard)
        return
    
    # Кнопка "Горизонт прогноза"
    if message.text == "📅 Горизонт прогноза":
        safe_print(f"📅 [{datetime.now().strftime('%H:%M:%S')}] {username} открыл меню горизонта прогноза")
        log_bot_action("Opening forecast menu")
        keyboard = get_forecast_menu()
        await message.answer("Выбери горизонт прогноза:", reply_markup=keyboard)
        return
    
    # Кнопка "Назад"
    if message.text == "◀️ Назад":
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(f"Главное меню:\n\n{status}", reply_markup=keyboard)
        return
    
    # Кнопка "Помощь"
    if message.text == "ℹ️ Помощь":
        await message.answer(get_help_text())
        return
    
    # Кнопка "О боте"
    if message.text == "📋 О боте":
        await message.answer(get_about_text())
        return
    
    # Кнопка "Перезапуск"
    if message.text == "🔄 Перезапуск":
        safe_print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] {username} запустил перезапуск бота")
        
        # Очищаем состояние пользователя
        old_state = state.copy()
        state.clear()
        state.update({"ticker": None, "amount": None, "forecast_days": 30, "mode": "normal", "temp_forecast": None})
        
        # Логируем что было сброшено
        if old_state.get("ticker") or old_state.get("amount") or old_state.get("temp_forecast"):
            safe_print(f"🧹 [{datetime.now().strftime('%H:%M:%S')}] Очищены настройки {username}: тикер={old_state.get('ticker')}, сумма=${old_state.get('amount')}")
        
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        
        # Получаем статистику тестов реальности
        statistics = await format_user_statistics()
        
        await message.answer(
            f"🔄 **ПЕРЕЗАПУСК ЗАВЕРШЕН**\n\n"
            f"✅ Все настройки сброшены\n"
            f"✅ Временные данные очищены\n"
            f"✅ Бот готов к работе\n\n"
            f"{status}\n\n"
            f"{statistics}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
        safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Перезапуск завершен для {username}")
        return
    
    # Кнопка "Испытание реальностью"
    if message.text == "🧪 Испытание реальностью":
        safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] {username} перешел в режим испытания реальностью")
        await show_user_tests_menu(message)
        return
    
    # Обработчики кнопок просмотра тестов (новый формат: "⏳ AAPL - Ожидает")
    status_icons = ["⏳", "🔬", "✅", "❓"]
    if any(message.text.startswith(icon) for icon in status_icons) and " - " in message.text:
        try:
            # Извлекаем тикер из кнопки "⏳ AAPL - Ожидает"
            ticker = message.text.split(" ")[1]
            
            # Находим тест по тикеру
            state = get_user_state(user_id)
            user_tests = get_user_all_tests(user_id)
            
            test_number = None
            for i, (test_id, test_data) in enumerate(user_tests.items(), 1):
                if test_data.get('ticker') == ticker:
                    test_number = i
                    break
            
            if test_number:
                await show_test_details(message, test_number)
                return
        except Exception as e:
            safe_print(f"❌ Ошибка обработки кнопки теста: {str(e)}")
            pass
    
    # Старый обработчик для совместимости
    if message.text.startswith("📊 Тест ") and "(" in message.text:
        # Извлекаем номер теста из кнопки "📊 Тест 1 (AAPL)"
        try:
            test_number = int(message.text.split(" ")[2])
            await show_test_details(message, test_number)
            return
        except:
            pass
    
    if message.text == "📈 Общая статистика":
        statistics = await format_user_statistics()
        await message.answer(statistics, reply_markup=get_main_menu(), parse_mode="Markdown")
        return
    
    if message.text == "🗑️ Удалить все тесты":
        user_tests = get_user_all_tests(user_id)
        
        if not user_tests:
            await message.answer("ℹ️ У вас нет активных тестов для удаления", reply_markup=get_main_menu())
            return
        
        # Подтверждение массового удаления
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        confirm_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🚨 ДА, УДАЛИТЬ ВСЕ"),
                    KeyboardButton(text="❌ Отмена")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        
        update_user_state(user_id, mode="confirming_delete_all")
        await message.answer(
            f"🚨 **ВНИМАНИЕ! МАССОВОЕ УДАЛЕНИЕ**\n\n"
            f"Вы собираетесь удалить **ВСЕ {len(user_tests)} тестов** реальности!\n\n"
            f"⚠️ **Это действие необратимо!**\n"
            f"• Будут удалены все прогнозы\n"
            f"• Будут удалены все торговые стратегии\n"
            f"• Будут удалены все результаты тестов\n"
            f"• Восстановление невозможно\n\n"
            f"Вы уверены?",
            reply_markup=confirm_keyboard,
            parse_mode="Markdown"
        )
        return
    
    if message.text == "🔙 К списку тестов":
        await show_user_tests_menu(message)
        return
    
    if message.text in ["🔙 Главное меню", "🏠 Главное меню"]:
        update_user_state(user_id, mode="normal")
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(f"Главное меню:\n\n{status}", reply_markup=keyboard)
        return
    
    # Обработчики действий с тестами
    if message.text.startswith("▶️ Выполнить тест #"):
        try:
            test_number = int(message.text.split("#")[1])
            state = get_user_state(user_id)
            tests_list = state.get("user_tests_list", [])
            if test_number <= len(tests_list):
                test_id = tests_list[test_number - 1]
                test_data = get_test_details(test_id, user_id)
                if test_data and test_data.get("status") == "ready":
                    await message.answer("⏳ Выполняем тест реальности... Это может занять несколько секунд.")
                    # TODO: Добавить выполнение теста
                    await message.answer("🔧 Функция выполнения теста в разработке", reply_markup=get_main_menu())
                else:
                    await message.answer("❌ Тест не готов к выполнению", reply_markup=get_main_menu())
        except:
            await message.answer("❌ Ошибка при выполнении теста", reply_markup=get_main_menu())
        return
    
    if message.text.startswith("📊 Результаты #"):
        try:
            test_number = int(message.text.split("#")[1])
            # TODO: Добавить показ результатов
            await message.answer("🔧 Функция просмотра результатов в разработке", reply_markup=get_main_menu())
        except:
            await message.answer("❌ Ошибка при загрузке результатов", reply_markup=get_main_menu())
        return
    
    if message.text.startswith("ℹ️ Инфо об ожидании #"):
        try:
            test_number = int(message.text.split("#")[1])
            state = get_user_state(user_id)
            tests_list = state.get("user_tests_list", [])
            if test_number <= len(tests_list):
                test_id = tests_list[test_number - 1]
                test_data = get_test_details(test_id, user_id)
                if test_data:
                    target_date = test_data.get("target_date", "")
                    try:
                        days_left = (datetime.strptime(target_date, "%Y-%m-%d") - datetime.now()).days
                        info_text = f"""
⏳ **ИНФОРМАЦИЯ ОБ ОЖИДАНИИ**

📈 **Тест:** {test_data.get('ticker', 'Unknown')} (#{test_number})
📅 **Целевая дата:** {target_date}
⏰ **Осталось дней:** {days_left}

💡 **Что происходит:**
Тест ожидает наступления целевой даты для получения реальных рыночных данных. После этой даты тест автоматически станет доступен для выполнения.

🔔 Вы получите уведомление когда тест будет готов!
"""
                        await message.answer(info_text, reply_markup=get_main_menu(), parse_mode="Markdown")
                    except:
                        await message.answer("❌ Ошибка при расчете времени ожидания", reply_markup=get_main_menu())
                else:
                    await message.answer("❌ Тест не найден", reply_markup=get_main_menu())
        except:
            await message.answer("❌ Ошибка при получении информации", reply_markup=get_main_menu())
        return
    
    if message.text.startswith("� Торговая стратегия #"):
        try:
            test_number = int(message.text.split("#")[1])
            state = get_user_state(user_id)
            tests_list = state.get("user_tests_list", [])
            if test_number <= len(tests_list):
                test_id = tests_list[test_number - 1]
                test_data = get_test_details(test_id, user_id)
                
                if test_data:
                    trading_recs = test_data.get('trading_recommendations', [])
                    expected_profit = test_data.get('expected_profit', 0)
                    profit_percent = test_data.get('profit_percent', 0)
                    amount = test_data.get('amount', 0)
                    ticker = test_data.get('ticker', 'Unknown')
                    
                    strategy_text = f"""
💼 **ПОЛНАЯ ТОРГОВАЯ СТРАТЕГИЯ**

📈 **Актив:** {ticker}
💰 **Инвестиции:** ${amount}
💵 **Ожидаемая прибыль:** ${expected_profit:.2f}
📊 **Доходность:** {profit_percent:+.2f}%
💎 **Итоговый капитал:** ${amount + expected_profit:.2f}

🎯 **ДЕТАЛЬНЫЕ РЕКОМЕНДАЦИИ:**
"""
                    
                    if trading_recs:
                        for i, rec in enumerate(trading_recs, 1):
                            if isinstance(rec, dict):
                                action = rec.get('action', 'N/A')
                                price = rec.get('price', 0)
                                date = rec.get('date', 'N/A')
                                shares = rec.get('shares', 0)
                                expected_profit = rec.get('expected_profit', 0)
                                reason = rec.get('reason', '')
                                
                                # Обрабатываем разные форматы цены (новый числовой и старый строковый)
                                if isinstance(price, str) and price.startswith('$'):
                                    price_value = float(price[1:])
                                elif isinstance(price, (int, float)):
                                    price_value = float(price)
                                else:
                                    price_value = 0
                                
                                strategy_text += f"""
{i}. **{date} - {action}**
   💵 Цена: ${price_value:.2f}
   📊 Количество: {shares:.2f} акций
   💰 Ожидаемая прибыль: ${expected_profit:.2f}
   💡 Обоснование: {reason}
"""
                    else:
                        strategy_text += "\n❓ Детальные рекомендации недоступны"
                    
                    # Оценка стратегии
                    strategy_text += f"\n💡 **ОЦЕНКА СТРАТЕГИИ:**\n"
                    if profit_percent > 10:
                        strategy_text += "🚀 **ВЫСОКОДОХОДНАЯ** - Отличный потенциал роста!"
                    elif profit_percent > 5:
                        strategy_text += "✅ **ПРИБЫЛЬНАЯ** - Хорошие возможности заработка"
                    elif profit_percent > 0:
                        strategy_text += "📈 **УМЕРЕННАЯ ПРИБЫЛЬ** - Стабильный рост"
                    else:
                        strategy_text += "⚠️ **УБЫТОЧНАЯ** - Рекомендуется избегать торговли"
                    
                    await message.answer(strategy_text, reply_markup=get_main_menu(), parse_mode="HTML")
                else:
                    await message.answer("❌ Данные теста не найдены", reply_markup=get_main_menu())
        except Exception as e:
            safe_print(f"❌ Ошибка показа торговой стратегии: {str(e)}")
            await message.answer("❌ Ошибка при загрузке торговой стратегии", reply_markup=get_main_menu())
        return
    
    if message.text.startswith("�🗑️ Удалить тест #"):
        try:
            test_number = int(message.text.split("#")[1])
            state = get_user_state(user_id)
            tests_list = state.get("user_tests_list", [])
            if test_number <= len(tests_list):
                test_id = tests_list[test_number - 1]
                
                # Подтверждение удаления
                from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
                confirm_keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text=f"✅ Да, удалить #{test_number}"),
                            KeyboardButton(text="❌ Отмена")
                        ]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                
                update_user_state(user_id, mode="confirming_delete", delete_test_id=test_id, delete_test_number=test_number)
                await message.answer(
                    f"🗑️ **ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ**\n\n"
                    f"Вы уверены, что хотите удалить тест #{test_number}?\n"
                    f"Это действие нельзя отменить.",
                    reply_markup=confirm_keyboard
                )
        except:
            await message.answer("❌ Ошибка при удалении теста", reply_markup=get_main_menu())
        return
    
    # Подтверждение удаления
    if state.get("mode") == "confirming_delete":
        if message.text.startswith("✅ Да, удалить #"):
            try:
                test_id = state.get("delete_test_id")
                test_number = state.get("delete_test_number")
                
                if delete_user_test(test_id, user_id):
                    await message.answer(
                        f"✅ Тест #{test_number} успешно удален!",
                        reply_markup=get_main_menu()
                    )
                    update_user_state(user_id, mode="normal")
                    safe_print(f"🗑️ [{datetime.now().strftime('%H:%M:%S')}] Пользователь {username} удалил тест #{test_number}")
                else:
                    await message.answer("❌ Ошибка при удалении теста", reply_markup=get_main_menu())
            except:
                await message.answer("❌ Ошибка при удалении теста", reply_markup=get_main_menu())
        else:
            await message.answer("Операция отменена", reply_markup=get_main_menu())
            update_user_state(user_id, mode="normal")
        return
    
    # Подтверждение массового удаления всех тестов
    if state.get("mode") == "confirming_delete_all":
        if message.text == "🚨 ДА, УДАЛИТЬ ВСЕ":
            try:
                deleted_info = delete_all_user_tests(user_id)
                
                if deleted_info["total"] > 0:
                    result_text = f"""
🗑️ **МАССОВОЕ УДАЛЕНИЕ ЗАВЕРШЕНО**

✅ **Удалено тестов:** {deleted_info['total']}
📜 **Старых тестов:** {deleted_info['old_tests']}
🆕 **Новых тестов:** {deleted_info['new_tests']}

🧹 Все ваши тесты реальности были успешно удалены.
💡 Вы можете создать новые тесты после получения прогнозов.
"""
                    await message.answer(result_text, reply_markup=get_main_menu())
                    safe_print(f"🗑️ [{datetime.now().strftime('%H:%M:%S')}] Пользователь {username} удалил все тесты ({deleted_info['total']} шт.)")
                else:
                    await message.answer("ℹ️ Не найдено тестов для удаления", reply_markup=get_main_menu())
                
                update_user_state(user_id, mode="normal")
            except Exception as e:
                safe_print(f"❌ Ошибка массового удаления для {username}: {str(e)}")
                await message.answer("❌ Ошибка при удалении тестов", reply_markup=get_main_menu())
                update_user_state(user_id, mode="normal")
        else:
            await message.answer("Операция отменена. Все тесты сохранены.", reply_markup=get_main_menu())
            update_user_state(user_id, mode="normal")
        return
    
    # Обработка ответа на предложение создать тест реальности
    if state.get("mode") == "offering_reality_test":
        safe_print(f"🤝 [{datetime.now().strftime('%H:%M:%S')}] Вызываем handle_reality_test_offer_response для {username}")
        safe_print(f"📝 [{datetime.now().strftime('%H:%M:%S')}] Текст сообщения: '{text}'")
        safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] temp_forecast статус: {'ЕСТЬ' if state.get('temp_forecast') else 'ОТСУТСТВУЕТ'}")
        await handle_reality_test_offer_response(message, state)
        return
    
    # Обработка выбора даты (ПРИОРИТЕТ!)
    if state.get("mode") == "selecting_test_date" or state.get("mode") == "entering_custom_date":
        safe_print(f"🎯 [{datetime.now().strftime('%H:%M:%S')}] Вызываем handle_date_selection для {username}")
        await handle_date_selection(message, state)
        return
    
    # Обработка команд режима испытания реальностью  
    if state.get("mode") == "reality_test":
        safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] Вызываем handle_reality_test_commands для {username}")
        await handle_reality_test_commands(message, state)
        return
    
    # 🧪 СПЕЦИАЛЬНАЯ ОТЛАДОЧНАЯ КОМАНДА ДЛЯ ТЕСТИРОВАНИЯ
    if message.text == "🧪 Тест":
        safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] {username} запросил тестовое создание теста реальности")
        
        # Создаем тестовый прогноз
        import numpy as np
        test_forecast = {
            "ticker": "NVDA",
            "amount": 100,
            "model_name": "LSTM_TEST", 
            "predictions": [190.0, 195.0, 200.0, 195.0, 185.0],
            "forecast_days": 5,
            "trading_recommendations": [
                {
                    "action": "КУПИТЬ",
                    "date": "2026-01-10", 
                    "price": 190.0,
                    "quantity": 0.52,
                    "profit": 0
                },
                {
                    "action": "ПРОДАТЬ",
                    "date": "2026-01-12",
                    "price": 200.0, 
                    "quantity": 0.52,
                    "profit": 5.2
                }
            ],
            "expected_profit": 5.2,
            "profit_percent": 5.2,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Сохраняем в состояние
        state["temp_forecast"] = test_forecast
        state["mode"] = "offering_reality_test"
        update_user_state(user_id, temp_forecast=test_forecast, mode="offering_reality_test")
        
        # Предлагаем создать тест
        await offer_reality_test(message, state)
        return

    # Выбор тикера из списка
    if message.text in POPULAR_TICKERS:
        old_ticker = state["ticker"]
        state["ticker"] = POPULAR_TICKERS[message.text]
        safe_print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] {username} выбрал тикер: {old_ticker} → {state['ticker']}")
        
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(
            f"✅ Выбран тикер: {state['ticker']}\n\n{status}",
            reply_markup=keyboard
        )
        return
    
    # Выбор суммы из кнопок
    if message.text in ["💵 100", "💵 200", "💵 500", "💵 1000"]:
        old_amount = state["amount"]
        state["amount"] = int(message.text.split()[1])
        safe_print(f"💰 [{datetime.now().strftime('%H:%M:%S')}] {username} выбрал сумму: ${old_amount} → ${state['amount']}")
        
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(
            f"✅ Выбрана сумма: ${state['amount']}\n\n{status}",
            reply_markup=keyboard
        )
        return
    
    # Выбор горизонта прогноза
    if message.text in ["📅 5 дней", "📅 10 дней", "📅 15 дней", "📅 20 дней", "📅 25 дней", "📅 30 дней"]:
        state["forecast_days"] = int(message.text.split()[1])
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(
            f"✅ Выбран горизонт прогноза: {state['forecast_days']} дней\n\n{status}",
            reply_markup=keyboard
        )
        return
    
    # Ввод своей суммы
    if message.text == "✏️ Своя":
        await message.answer("Отправь сумму числом, например: 1500")
        return
    
    # Попытка распарсить число как сумму
    try:
        amount = int(message.text)
        if 1 <= amount <= 1000000:
            state["amount"] = amount
            keyboard = get_main_menu()
            status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
            await message.answer(
                f"✅ Выбрана сумма: ${state['amount']}\n\n{status}",
                reply_markup=keyboard
            )
            return
    except ValueError:
        pass
    
    # Кнопка "Анализ"
    if message.text == "📈 Анализ":
        if not state["ticker"]:
            safe_print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] {username} пытается запустить анализ без тикера")
            await message.answer("❌ Сначала выбери тикер!")
            return
        if not state["amount"]:
            safe_print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] {username} пытается запустить анализ без суммы")
            await message.answer("❌ Сначала выбери сумму инвестиций!")
            return
        
        # Логируем начало анализа
        safe_print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] {username} запускает анализ:")
        safe_print(f"    📊 Тикер: {state['ticker']}")
        safe_print(f"    💰 Сумма: ${state['amount']}")
        safe_print(f"    📅 Горизонт: {state['forecast_days']} дней")
        
        # Уведомляем пользователя о начале процесса
        await message.answer("🚀 Запуск анализа акций! Подготовка данных...")
        
        import time  # Для отслеживания времени
        start_time = time.time()
        
        try:
            ticker = state["ticker"]
            amount = state["amount"]
            forecast_days = state["forecast_days"]
            
            log_bot_action(f"Starting analysis for {ticker}, amount={amount}, forecast={forecast_days}")
            await message.answer("⏳ Загружаю данные и запускаю анализ...")
            safe_print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Начинаю анализ для {username}")
            
            # Показываем более подробный процесс загрузки
            await message.answer(f"📊 Загружаю данные для {ticker} за последние 2 года...")
            safe_print(f"📡 [{datetime.now().strftime('%H:%M:%S')}] Начало загрузки данных для {ticker}")
            data_start = time.time()
            
            try:
                df = get_finance_data(ticker)
                safe_print(f"📥 [{datetime.now().strftime('%H:%M:%S')}] Функция get_finance_data вызвана")
            except Exception as data_error:
                safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка в get_finance_data: {str(data_error)}")
                raise data_error
                
            if df is None:
                safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] get_finance_data вернула None для {ticker}")
                await message.answer(
                    f"❌ **Ошибка загрузки данных для {ticker}**\n\n"
                    f"Возможные причины:\n"
                    f"• Неверный тикер акции\n"
                    f"• Временные проблемы с Yahoo Finance\n"
                    f"• Проблемы с интернет соединением\n\n"
                    f"💡 **Попробуйте:**\n"
                    f"• Проверить правильность написания тикера\n"
                    f"• Выбрать другой тикер из списка\n"
                    f"• Повторить попытку через несколько минут"
                )
                return
            
            data_time = time.time() - data_start
            safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Данные успешно загружены: {len(df)} записей за {data_time:.1f}с")
            
            # Уведомляем пользователя об успешной загрузке
            await message.answer(f"✅ Данные загружены: {len(df)} записей за {len(df)} дней")
            
            # Проверка достаточности данных
            if len(df) < 100:
                safe_print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Недостаточно данных для {ticker}: {len(df)} дней")
                await message.answer(f"❌ Недостаточно данных для анализа. Получено только {len(df)} дней. Нужно минимум 100.")
                return
            
            safe_print(f"Data shape: {df.shape}, Days: {len(df)}")
            safe_print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] Начало создания каталога задачи")

            # Создаем каталог для задачи
            import os
            
            request_date = datetime.now().strftime("%Y-%m-%d")
            last_data_date = df.index[-1].strftime("%Y-%m-%d")
            task_folder = f"Tasks/{ticker}-{amount}-{request_date}-{last_data_date}"
            
            os.makedirs(task_folder, exist_ok=True)
            log_bot_action(f"Created task folder: {task_folder}")
            
            # Сохраняем данные котировок в CSV
            csv_path = os.path.join(task_folder, f"{ticker}_data.csv")
            df.to_csv(csv_path)
            safe_print(f"💾 [{datetime.now().strftime('%H:%M:%S')}] Данные сохранены в {csv_path}")
            log_bot_action(f"Saved data to {csv_path}")
            
            # Запускаем сравнение моделей
            await message.answer("🤖 Инициализация ИИ-моделей...")
            safe_print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Начало инициализации ML-моделей")
            model_start = time.time()
            
            # Уведомляем о начале обучения
            await message.answer("🧠 Обучаю модели прогнозирования (LSTM, GRU, Autoformer и др.)...")
            safe_print(f"🤖 [{datetime.now().strftime('%H:%M:%S')}] Запуск обучения моделей прогнозирования")
            
            try:
                best_model, second_best_model, comparison_data = compare_all_models(df, forecast_days, task_folder)
                model_time = time.time() - model_start
                safe_print(f"🏆 [{datetime.now().strftime('%H:%M:%S')}] Обучение завершено за {model_time:.1f}с. Лучшая модель: {best_model['model_name']}")
            except Exception as model_error:
                safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка в обучении моделей: {str(model_error)}")
                await message.answer("❌ Ошибка при обучении моделей. Попробуйте позже или выберите другой тикер.")
                raise model_error
            
            # Отладка: проверяем прогнозы
            safe_print(f"Best predictions shape: {best_model['predictions'].shape}")
            safe_print(f"Best predictions: {best_model['predictions'][:5]}...")
            safe_print(f"Min: {best_model['predictions'].min()}, Max: {best_model['predictions'].max()}")
            safe_print(f"📈 [{datetime.now().strftime('%H:%M:%S')}] Начало создания графиков")
            
            # Сохраняем график исторических данных
            img_path = generate_graph(df, ticker, task_folder)
            log_bot_action(f"Generated historical graph for {ticker}")
            
            # Создаем графики для лучшей модели
            forecast_img_path = generate_forecast_graph(
                df, ticker, best_model['predictions'], 
                best_model['model_name'], task_folder
            )
            log_bot_action(f"Generated full forecast graph for {ticker}")
            
            forecast_zoomed_path = generate_forecast_graph_zoomed(
                df, ticker, best_model['predictions'], 
                best_model['model_name'], task_folder
            )
            log_bot_action(f"Generated zoomed forecast graph for {ticker}")

            # Отправляем результаты лучшей модели
            total_time = time.time() - start_time
            safe_print(f"🏁 [{datetime.now().strftime('%H:%M:%S')}] АНАЛИЗ ЗАВЕРШЕН за {total_time:.1f} секунд")
            
            result_text = (
                f"📊 Анализ завершен!\n\n"
                f"🥇 Лучшая модель: {best_model['model_name']}\n"
                f"📉 RMSE: {best_model['rmse']:.2f}\n"
                f"📈 MAPE: {best_model['mape']:.2f}%\n\n"
                f"💰 Сумма инвестиций: ${amount}\n"
                f"📅 Горизонт прогноза: {forecast_days} дней\n\n"
                f"Прогноз цены на {forecast_days} дней:\n"
                f"Начальная: ${best_model['predictions'][0]:.2f}\n"
                f"Конечная: ${best_model['predictions'][-1]:.2f}\n"
                f"Изменение: {((best_model['predictions'][-1] / df['Close'].iloc[-1] - 1) * 100):.2f}%\n\n"
                f"⏱️ Время анализа: {total_time:.1f} секунд\n"
                f"Результаты сохранены в: {task_folder}"
            )
            
            # Отправляем полный график лучшей модели
            forecast_photo = FSInputFile(forecast_img_path)
            await message.answer_photo(photo=forecast_photo, caption=result_text)
            safe_print(f"🖼️ [{datetime.now().strftime('%H:%M:%S')}] Отправлен полный график лучшей модели")
            
            # Отправляем увеличенный график лучшей модели
            forecast_zoomed_photo = FSInputFile(forecast_zoomed_path)
            await message.answer_photo(photo=forecast_zoomed_photo, 
                                      caption=f"🏆 {best_model['model_name']} - Детальный вид (60 дней + прогноз)")
            safe_print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] Отправлен детальный график")
            
            # Создаем и отправляем графики для второй лучшей модели
            if second_best_model:
                forecast_img_path_2 = generate_forecast_graph(
                    df, ticker, second_best_model['predictions'], 
                    second_best_model['model_name'], task_folder
                )
                
                forecast_zoomed_path_2 = generate_forecast_graph_zoomed(
                    df, ticker, second_best_model['predictions'], 
                    second_best_model['model_name'], task_folder
                )
                
                result_text_2 = (
                    f"🥈 Вторая лучшая модель: {second_best_model['model_name']}\n"
                    f"📉 RMSE: {second_best_model['rmse']:.2f}\n"
                    f"📈 MAPE: {second_best_model['mape']:.2f}%\n\n"
                    f"Прогноз цены на {forecast_days} дней:\n"
                    f"Начальная: ${second_best_model['predictions'][0]:.2f}\n"
                    f"Конечная: ${second_best_model['predictions'][-1]:.2f}\n"
                    f"Изменение: {((second_best_model['predictions'][-1] / df['Close'].iloc[-1] - 1) * 100):.2f}%"
                )
                
                # Отправляем полный график второй модели
                forecast_photo_2 = FSInputFile(forecast_img_path_2)
                await message.answer_photo(photo=forecast_photo_2, caption=result_text_2)
                
                # Отправляем увеличенный график второй модели
                forecast_zoomed_photo_2 = FSInputFile(forecast_zoomed_path_2)
                await message.answer_photo(photo=forecast_zoomed_photo_2, 
                                          caption=f"🥈 {second_best_model['model_name']} - Детальный вид (60 дней + прогноз)")
            
            # Отправляем сравнение всех моделей
            models_text = "📊 Сравнение моделей:\n\n"
            for model in comparison_data['models']:
                models_text += f"{model['name']}: RMSE={model['rmse']:.2f}, MAPE={model['mape']:.2f}%\n"
            
            await message.answer(models_text)
            
            # Генерируем торговые рекомендации
            await message.answer("💡 Генерирую торговые рекомендации...")
            
            import pandas as pd
            from datetime import timedelta
            forecast_dates = pd.date_range(
                start=df.index[-1] + timedelta(days=1),
                periods=forecast_days,
                freq='D'
            )
            
            current_price = df['Close'].iloc[-1]
            recommendations, expected_profit, trades = calculate_trading_strategy(
                best_model['predictions'],
                forecast_dates,
                amount,
                current_price
            )
            
            # Рассчитываем процент прибыли
            profit_percent = (expected_profit / amount) * 100 if amount > 0 else 0
            
            # Сохраняем рекомендации
            rec_file, csv_file = save_recommendations_to_file(
                recommendations, expected_profit, profit_percent,
                amount, ticker, task_folder
            )
            
            # Отправляем рекомендации в новом цветном формате логирования
            rec_text = generate_recommendations_text(
                recommendations, expected_profit, profit_percent,
                amount, ticker
            )
            
            # Разбиваем на части если текст слишком длинный
            if len(rec_text) > 4000:
                # Разбиваем по строкам чтобы не разрывать HTML теги
                lines = rec_text.split('\n')
                parts = []
                current_part = ""
                
                for line in lines:
                    if len(current_part) + len(line) + 1 > 4000:
                        if current_part:
                            parts.append(current_part.strip())
                        current_part = line
                    else:
                        current_part += "\n" + line if current_part else line
                
                if current_part:
                    parts.append(current_part.strip())
                
                for part in parts:
                    await message.answer(part)
            else:
                await message.answer(rec_text)
            
            # Сохраняем прогноз для возможного испытания реальностью
            state["temp_forecast"] = {
                "ticker": ticker,
                "amount": amount,
                "model_name": best_model['model_name'],
                "predictions": best_model['predictions'],
                "forecast_days": forecast_days,
                "trading_recommendations": recommendations,  # Добавляем рекомендации
                "expected_profit": expected_profit,
                "profit_percent": profit_percent,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] Прогноз сохранен для возможного тестирования")
            log_bot_action(f"Saved temporary forecast for reality testing: {ticker}")
            
            # Предлагаем создать тест реальности
            await offer_reality_test(message, state)
            
        except Exception as e:
            error_msg = str(e)
            safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка в анализе для {username}: {error_msg}")
            log_bot_action(f"Error in analysis: {error_msg}")
            
            # Более детальное логирование для отладки
            import traceback
            detailed_error = traceback.format_exc()
            safe_print(f"Analysis error details: {detailed_error}")
            
            # Разные сообщения для разных типов ошибок
            if "download" in error_msg.lower() or "yahoo" in error_msg.lower():
                user_msg = (
                    f"❌ <b>Ошибка загрузки данных</b>\n\n"
                    f"Проблема с получением данных для {ticker}\n\n"
                    f"🔧 <b>Попробуйте:</b>\n"
                    f"• Выбрать другой тикер\n"
                    f"• Повторить через несколько минут\n"
                    f"• Использовать команду /debug для диагностики\n\n"
                    f"🆘 Если проблема повторяется - обратитесь к администратору"
                )
            elif "model" in error_msg.lower():
                user_msg = (
                    f"❌ <b>Ошибка в модели прогнозирования</b>\n\n"
                    f"Проблема при обучении моделей для {ticker}\n\n"
                    f"💡 <b>Рекомендации:</b>\n"
                    f"• Попробуйте другой тикер\n"
                    f"• Уменьшите горизонт прогноза\n"
                    f"• Повторите попытку позже"
                )
            else:
                user_msg = (
                    f"❌ <b>Произошла ошибка</b>\n\n"
                    f"Не удалось выполнить анализ для {ticker}\n\n"
                    f"🔄 <b>Действия:</b>\n"
                    f"• Попробуйте другой тикер или сумму\n"
                    f"• Используйте /debug для проверки системы\n"
                    f"• Перезапустите бота командой /start"
                )
            
            await message.answer(user_msg)
        return

    # Обработка кнопки "Нет, спасибо" вне контекста
    if message.text == "❌ Нет, спасибо":
        safe_print(f"🚫 [{datetime.now().strftime('%H:%M:%S')}] {username} нажал 'Нет, спасибо' без контекста")
        await message.answer(
            f"👌 **ПОНЯТНО!**\n\n"
            f"Похоже, эта кнопка осталась от предыдущего предложения создать тест.\n\n"
            f"🔄 Используйте основное меню для управления ботом:"
        )
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(f"{status}", reply_markup=keyboard)
        return
    
    # Проверяем, не ввел ли пользователь дату в неправильном контексте
    import re
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(date_pattern, message.text.strip()):
        safe_print(f"📅 [{datetime.now().strftime('%H:%M:%S')}] {username} ввел дату '{message.text}' не в том контексте")
        await message.answer(
            f"📅 **ДАТА ОБНАРУЖЕНА: {message.text}**\n\n"
            f"❓ Похоже, вы пытаетесь ввести дату для теста реальности.\n\n"
            f"🔄 **Правильная последовательность:**\n"
            f"1. Сначала сделайте анализ акций\n"
            f"2. Перейдите в '🧪 Испытание реальностью'\n"
            f"3. Нажмите '🔬 Создать тест'\n"
            f"4. Выберите дату из предложенных или введите свою\n\n"
            f"💡 Дата может быть введена только в режиме создания теста!"
        )
        return
    
    # Если ничего не подошло
    keyboard = get_main_menu()
    status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
    await message.answer(
        f"Используй кнопки меню для управления ботом\n\n{status}",
        reply_markup=keyboard
    )

async def handle_reality_test_commands(message: types.Message, state: dict):
    """Обработка команд режима испытания реальностью"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    text = message.text
    
    safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] {username} в режиме тестирования: {text}")
    
    # Кнопка "Назад" - возврат в обычный режим
    if text == "◀️ Назад":
        safe_print(f"↩️ [{datetime.now().strftime('%H:%M:%S')}] {username} вышел из режима тестирования")
        state["mode"] = "normal"
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(f"Возвращение в главное меню:\n\n{status}", reply_markup=keyboard)
        return
    
    # Кнопка "Создать тест"
    if text == "🔬 Создать тест":
        if not state.get("temp_forecast"):
            safe_print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] {username} пытается создать тест без прогноза")
            
            # Проверяем, есть ли у пользователя настроенные параметры
            has_settings = state.get("ticker") and state.get("amount")
            
            if has_settings:
                # У пользователя есть настройки, но нет свежего прогноза
                await message.answer(
                    f"❌ **ДЛЯ СОЗДАНИЯ ТЕСТА НУЖЕН СВЕЖИЙ ПРОГНОЗ**\n\n"
                    f"📊 Ваши текущие настройки:\n"
                    f"• Тикер: {state.get('ticker', 'не выбрано')}\n"
                    f"• Сумма: ${state.get('amount', 'не выбрано')}\n"
                    f"• Горизонт: {state.get('forecast_days', 30)} дней\n\n"
                    f"🔄 **ДЕЙСТВИЯ:**\n"
                    f"1. Нажмите '◀️ Назад' для возврата в главное меню\n"
                    f"2. Нажмите '📈 Анализ' для создания нового прогноза\n"
                    f"3. После анализа выберите 'Создать тест реальности'\n\n"
                    f"💡 Тест можно создать только сразу после анализа!"
                )
            else:
                # У пользователя нет даже базовых настроек
                await message.answer(
                    f"❌ **НАСТРОЙКИ НЕ ЗАВЕРШЕНЫ**\n\n"
                    f"📋 Для создания теста сначала:\n\n"
                    f"1. 🔍 Выберите тикер акции\n"
                    f"2. 💵 Укажите сумму инвестиций\n"
                    f"3. 📈 Сделайте анализ и прогноз\n"
                    f"4. После анализа сразу создайте тест\n\n"
                    f"🔄 Нажмите '◀️ Назад' для возврата в главное меню"
                )
            return
        
        safe_print(f"📅 [{datetime.now().strftime('%H:%M:%S')}] {username} создает тест для {state['temp_forecast']['ticker']}")
        keyboard = get_test_date_menu()
        await message.answer(
            "📅 **ВЫБЕРИТЕ ДАТУ ДЛЯ ПРОВЕРКИ ПРОГНОЗА:**\n\n"
            "В указанную дату бот автоматически загрузит реальные котировки и сравнит их с прогнозом.",
            reply_markup=keyboard
        )
        state["mode"] = "selecting_test_date"
        return
    
    # Кнопка "Статус тестов"
    if text == "📊 Статус тестов":
        safe_print(f"📊 [{datetime.now().strftime('%H:%M:%S')}] {username} запросил статус тестов")
        current_test = get_user_reality_test(user_id)
        if current_test:
            test_status = format_test_status(current_test)
            await message.answer(test_status)
        else:
            await message.answer(
                "❌ **У вас нет активных тестов реальности**\n\n"
                "💡 Чтобы создать тест:\n"
                "1. Вернитесь в главное меню\n"
                "2. Сделайте анализ акции\n"
                "3. Вернитесь сюда и нажмите '🔬 Создать тест'"
            )
        return
    
    # Кнопка "Мои тесты" - новая функция
    if text == "🔍 Мои тесты":
        safe_print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] {username} запросил свои тесты")
        await show_user_tests(message, user_id)
        return
    
    # Кнопка "Отменить тест"
    if text == "🗑️ Отменить тест":
        if remove_reality_test(user_id):
            safe_print(f"🗑️ [{datetime.now().strftime('%H:%M:%S')}] {username} отменил тест")
            await message.answer("✅ Тест реальности отменен")
        else:
            safe_print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] {username} пытается отменить несуществующий тест")
            await message.answer("❌ У вас нет активных тестов для отмены")
        return
    
    # Кнопка "Выполнить готовые"
    if text == "📈 Выполнить готовые":
        safe_print(f"🏃 [{datetime.now().strftime('%H:%M:%S')}] {username} запускает выполнение готовых тестов")
        ready_tests = check_ready_tests()
        user_ready_tests = [(uid, test) for uid, test in ready_tests if uid == user_id]
        
        if not user_ready_tests:
            safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] У {username} нет готовых тестов")
            await message.answer("❌ У вас нет готовых к выполнению тестов")
            return
        
        for user_test_id, test_data in user_ready_tests:
            safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] Выполняю тест для {username}: {test_data['ticker']}")
            await message.answer("⏳ Выполняю тест реальности...")
            success, report, metrics = await execute_reality_test(user_test_id, test_data)
            
            if success:
                safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Тест успешно выполнен для {username}")
                # Разбиваем на части если слишком длинный
                if len(report) > 4000:
                    parts = [report[i:i+4000] for i in range(0, len(report), 4000)]
                    for part in parts:
                        await message.answer(part)
                else:
                    await message.answer(report)
                
                # Удаляем выполненный тест
                remove_reality_test(user_test_id)
                await message.answer("✅ Тест завершен и удален из активных")
            else:
                safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка выполнения теста для {username}")
                await message.answer(report)
        return
    
    # Если команда не распознана
    safe_print(f"❓ [{datetime.now().strftime('%H:%M:%S')}] {username} отправил нераспознанную команду в режиме тестирования: {text}")
    keyboard = get_reality_test_menu()
    await message.answer("❓ Используйте кнопки меню", reply_markup=keyboard)

async def handle_date_selection(message: types.Message, state: dict):
    """Обработка выбора даты для теста"""
    from datetime import datetime, timedelta
    
    text = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    safe_print(f"🎯 [{datetime.now().strftime('%H:%M:%S')}] ВХОД В handle_date_selection для {username}")
    safe_print(f"📅 [{datetime.now().strftime('%H:%M:%S')}] {username} обрабатывает выбор даты: '{text}'")
    safe_print(f"🔧 Режим пользователя: {state.get('mode')}")
    safe_print(f"🧪 temp_forecast: {'есть' if state.get('temp_forecast') else 'НЕТ!'}")
    safe_print(f"🧮 Длина текста: {len(text)} символов")
    safe_print(f"📊 Первые 10 символов: '{text[:10] if len(text) >= 10 else text}'")
    
    if text.startswith("📅 "):
        safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Текст начинается с '📅 '")
    else:
        safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Текст НЕ начинается с '📅 '. Начинается с: '{text[:5]}'")
    
    if text == "◀️ Назад":
        state["mode"] = "reality_test"
        keyboard = get_reality_test_menu()
        await message.answer("Возвращение в меню тестирования", reply_markup=keyboard)
        return
    
    # Кнопка "Своя дата"
    if text == "✏️ Своя дата":
        await message.answer(
            "📅 Введите дату в формате YYYY-MM-DD\n"
            "Например: 2026-01-15\n\n"
            "⚠️ Дата должна быть не ранее завтрашнего дня"
        )
        update_user_state(user_id, mode="entering_custom_date")
        return
    
    target_date = None
    
    # Обработка выбора предложенной даты
    if text.startswith("📅 "):
        target_date = text[2:]  # Убираем эмодзи и пробел (📅 - это 2 символа)
        safe_print(f"🎯 [{datetime.now().strftime('%H:%M:%S')}] Извлечена дата из кнопки: {target_date}")
    
    # Обработка ввода своей даты
    elif state.get("mode") == "entering_custom_date":
        target_date = text.strip()
        safe_print(f"✏️ [{datetime.now().strftime('%H:%M:%S')}] Введена пользователем дата: {target_date}")
    else:
        safe_print(f"❓ [{datetime.now().strftime('%H:%M:%S')}] Неожиданный текст: {text}")
        return  # Выходим, если не распознали команду
    
    if target_date:
        safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Начинаем обработку даты: {target_date}")
        # Валидация даты
        try:
            from datetime import datetime, timedelta
            test_date = datetime.strptime(target_date, "%Y-%m-%d")
            tomorrow = datetime.now() + timedelta(days=1)
            
            if test_date < tomorrow:
                await message.answer("❌ Дата должна быть не ранее завтрашнего дня")
                return
            
            # Создаем тест
            temp_forecast = state.get("temp_forecast")
            safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] Проверка temp_forecast:")
            safe_print(f"   temp_forecast существует: {'ДА' if temp_forecast else 'НЕТ'}")
            if temp_forecast:
                safe_print(f"   temp_forecast тип: {type(temp_forecast)}")
                safe_print(f"   temp_forecast ключи: {list(temp_forecast.keys()) if isinstance(temp_forecast, dict) else 'НЕ СЛОВАРЬ'}")
                if isinstance(temp_forecast, dict):
                    safe_print(f"   ticker: {temp_forecast.get('ticker', 'НЕТ')}")
                    safe_print(f"   amount: {temp_forecast.get('amount', 'НЕТ')}")
                    safe_print(f"   model_name: {temp_forecast.get('model_name', 'НЕТ')}")
                    safe_print(f"   predictions тип: {type(temp_forecast.get('predictions', 'НЕТ'))}")
            
            if not temp_forecast:
                safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] temp_forecast отсутствует для {username}")
                await message.answer("❌ Ошибка: прогноз не найден")
                return
            
            # Уведомляем пользователя о начале процесса
            await message.answer("⏳ Создаю тест реальности...")
            safe_print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Начинаем создание теста для {username}")
            
            # Создаем тест с новой системой
            safe_print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] Вызываем create_structured_reality_test")
            test_result = await create_structured_reality_test(
                user_id,
                username,
                temp_forecast,
                target_date,
                message
            )
            
            safe_print(f"🎯 [{datetime.now().strftime('%H:%M:%S')}] Результат create_structured_reality_test:")
            safe_print(f"   success: {test_result.get('success', 'НЕТ КЛЮЧА')}")
            safe_print(f"   error: {test_result.get('error', 'НЕТ ОШИБКИ')}")
            safe_print(f"   test_id: {test_result.get('test_id', 'НЕТ ID')}")
            
            if test_result["success"]:
                await message.answer(
                    f"✅ **ТЕСТ РЕАЛЬНОСТИ СОЗДАН!**\n\n"
                    f"📁 **Сохранено в:** {test_result['folder']}\n"
                    f"📈 **Актив:** {temp_forecast['ticker']}\n"
                    f"🤖 **Модель:** {temp_forecast['model_name']}\n"
                    f"📅 **Целевая дата:** {target_date}\n"
                    f"💰 **Сумма:** ${temp_forecast['amount']}\n"
                    f"📊 **Дней прогноза:** {len(temp_forecast['predictions'])}\n"
                    f"📋 **ID теста:** {test_result['test_id']}\n\n"
                    f"🔮 **Результат будет готов:** {target_date}\n"
                    f"📱 **Отслеживание:** Используйте '🔍 Мои тесты' для проверки статуса\n\n"
                    f"⏰ Я автоматически уведомлю вас когда результат будет готов!"
                )
                
                # Показываем дополнительную информацию
                await message.answer(
                    f"📊 **ДЕТАЛИ ПРОГНОЗА:**\n"
                    f"🎯 Начальная цена: ${temp_forecast['predictions'][0]:.2f}\n"
                    f"🎯 Конечная цена: ${temp_forecast['predictions'][-1]:.2f}\n"
                    f"📈 Ожидаемое изменение: {((temp_forecast['predictions'][-1] / temp_forecast['predictions'][0] - 1) * 100):.2f}%\n\n"
                    f"🗂️ Все данные сохранены для последующей проверки"
                )
                
                # Очищаем временные данные и возвращаемся в главное меню
                state["temp_forecast"] = None
                state["mode"] = "normal"
                
                keyboard = get_main_menu()
                status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
                await message.answer(
                    f"🔙 **Возвращение в главное меню**\n\n{status}", 
                    reply_markup=keyboard
                )
            else:
                await message.answer("❌ Ошибка при создании теста")
                
        except ValueError:
            await message.answer("❌ Неверный формат даты. Используйте YYYY-MM-DD")
        except Exception as e:
            safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Ошибка в создании теста: {str(e)}")
            await message.answer(f"❌ Ошибка: {str(e)}")

async def offer_reality_test(message: types.Message, state: dict):
    """Предлагает пользователю создать тест реальности после анализа"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    temp_forecast = state.get("temp_forecast")
    
    if not temp_forecast:
        return
    
    safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] Предлагаем {username} создать тест реальности")
    
    # Создаем клавиатуру с предложением
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Да, создать тест"),
                KeyboardButton(text="❌ Нет, спасибо")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    update_user_state(user_id, mode="offering_reality_test")
    
    offer_text = (
        f"🧪 **СОЗДАТЬ ТЕСТ РЕАЛЬНОСТИ?**\n\n"
        f"📈 Актив: {temp_forecast['ticker']}\n"
        f"🤖 Модель: {temp_forecast['model_name']}\n"
        f"📅 Прогноз: {temp_forecast['forecast_days']} дней\n"
        f"💰 Сумма: ${temp_forecast['amount']}\n\n"
        f"🔬 Тест реальности сравнит этот прогноз с фактическими данными в будущем.\n\n"
        f"Хотите создать тест?"
    )
    
    await message.answer(offer_text, reply_markup=keyboard)

async def handle_reality_test_offer_response(message: types.Message, state: dict):
    """Обрабатывает ответ на предложение создать тест реальности"""
    from datetime import datetime
    text = message.text.strip() if message.text else ""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] {username} ответил на предложение теста: '{text}'")
    safe_print(f"🔧 [{datetime.now().strftime('%H:%M:%S')}] Текущий режим: {state.get('mode')}")
    safe_print(f"🧪 [{datetime.now().strftime('%H:%M:%S')}] temp_forecast: {'есть' if state.get('temp_forecast') else 'НЕТ!'}")
    safe_print(f"📏 [{datetime.now().strftime('%H:%M:%S')}] Длина текста: {len(text)} символов")
    
    if text == "✅ Да, создать тест":
        safe_print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] {username} выбрал создать тест")
        # Переходим к выбору даты
        state["mode"] = "selecting_test_date"
        safe_print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Режим изменен на: selecting_test_date")
        
        keyboard = get_test_date_menu()
        await message.answer(
            "📅 **ВЫБЕРИТЕ ДАТУ ДЛЯ ПРОВЕРКИ ПРОГНОЗА:**\n\n"
            "В указанную дату бот автоматически загрузит реальные котировки и сравнит их с прогнозом.",
            reply_markup=keyboard
        )
        safe_print(f"📅 [{datetime.now().strftime('%H:%M:%S')}] {username} переходит к выбору даты теста")
        
    elif text == "❌ Нет, спасибо":
        safe_print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] {username} отказался от создания теста")
        # Возвращаемся в главное меню
        state["mode"] = "normal"
        state["temp_forecast"] = None  # Очищаем временный прогноз
        keyboard = get_main_menu()
        status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
        await message.answer(
            f"👌 **Понятно!**\n\n"
            f"Прогноз сохранен, тест реальности не создаем.\n\n"
            f"{status}",
            reply_markup=keyboard
        )
        
    else:
        safe_print(f"❓ [{datetime.now().strftime('%H:%M:%S')}] {username} отправил неожиданный ответ: '{text}'")
        safe_print(f"🔍 [{datetime.now().strftime('%H:%M:%S')}] Проверяем альтернативные варианты...")
        
        # Проверяем альтернативные варианты
        if "да" in text.lower() and "создать" in text.lower():
            safe_print(f"🔧 [{datetime.now().strftime('%H:%M:%S')}] Найдено альтернативное совпадение для 'Да'")
            # Обрабатываем как положительный ответ
            state["mode"] = "selecting_test_date"
            keyboard = get_test_date_menu()
            await message.answer(
                "📅 **ВЫБЕРИТЕ ДАТУ ДЛЯ ПРОВЕРКИ ПРОГНОЗА:**\n\n"
                "В указанную дату бот автоматически загрузит реальные котировки и сравнит их с прогнозом.",
                reply_markup=keyboard
            )
            return
            
        elif "нет" in text.lower() or "спасибо" in text.lower():
            safe_print(f"🔧 [{datetime.now().strftime('%H:%M:%S')}] Найдено альтернативное совпадение для 'Нет'")
            # Обрабатываем как отрицательный ответ
            state["mode"] = "normal"
            state["temp_forecast"] = None
            keyboard = get_main_menu()
            status = get_status_message(state["ticker"], state["amount"], state["forecast_days"])
            await message.answer(
                f"👌 **Понятно!**\n\n"
                f"Прогноз сохранен, тест реальности не создаем.\n\n"
                f"{status}",
                reply_markup=keyboard
            )
            return
        
        # Если ничего не подошло, показываем кнопки еще раз
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="✅ Да, создать тест"),
                    KeyboardButton(text="❌ Нет, спасибо")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            f"❓ **Неожиданный ответ: '{text}'**\n\n"
            f"Пожалуйста, выберите один из вариантов:",
            reply_markup=keyboard
        )

async def main():
    safe_print("🚀 Бот запущен и ожидает сообщения...")
    safe_print(f"📅 Текущая дата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Загружаем состояния пользователей при запуске
    load_user_states()
    
    log_bot_action("Bot started")
    
    # Получаем статистику всех тестов реальности
    safe_print("📊 Анализ статистики тестов реальности...")
    stats = get_reality_tests_statistics()
    
    safe_print("=" * 60)
    safe_print("📈 СТАТИСТИКА ТЕСТОВ РЕАЛЬНОСТИ:")
    safe_print(f"🔬 Всего тестов: {stats['total_count']}")
    safe_print(f"⏳ Ожидают наступления даты: {stats['waiting_count']}")
    safe_print(f"🔬 Готовы к выполнению: {stats['ready_count']}")
    safe_print(f"✅ Уже выполнены: {stats['completed_count']}")
    
    if stats['old_tests']['waiting'] > 0 or stats['old_tests']['ready'] > 0:
        safe_print(f"📜 Старые тесты: ожидают {stats['old_tests']['waiting']}, готовы {stats['old_tests']['ready']}")
    
    if stats['new_tests']['waiting'] > 0 or stats['new_tests']['ready'] > 0 or stats['new_tests']['completed'] > 0:
        safe_print(f"🆕 Новые тесты: ожидают {stats['new_tests']['waiting']}, готовы {stats['new_tests']['ready']}, выполнены {stats['new_tests']['completed']}")
    safe_print("=" * 60)
    
    # Проверяем готовые тесты при запуске
    safe_print("🔍 Проверка готовых тестов реальности...")
    ready_tests = check_ready_tests()
    if ready_tests:
        safe_print(f"📊 Найдено {len(ready_tests)} готовых тестов реальности")
        for user_id, test_data in ready_tests:
            try:
                safe_print(f"📨 Уведомляем пользователя ID:{user_id} о готовом тесте для {test_data['ticker']}")
                await bot.send_message(
                    user_id, 
                    f"🧪 **ТЕСТ РЕАЛЬНОСТИ ГОТОВ!**\n\n"
                    f"Ваш тест для актива {test_data['ticker']} готов к выполнению.\n"
                    f"Перейдите в 'Испытание реальностью' → 'Выполнить готовые'"
                )
            except Exception as e:
                safe_print(f"❌ Ошибка при уведомлении пользователя ID:{user_id}: {str(e)}")
    else:
        safe_print("✅ Готовых тестов не найдено")
    
    safe_print("🎯 Бот готов к работе!")
    safe_print("=" * 50)
    
    try:
        safe_print("🔄 Запуск цикла polling...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        safe_print("⏹️ Бот остановлен пользователем")
    except Exception as e:
        safe_print(f"❌ Критическая ошибка в боте: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        safe_print("👋 Бот остановлен")
    except Exception as e:
        safe_print(f"❌ Ошибка запуска: {str(e)}")
        import traceback
        traceback.print_exc()
