from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Популярные тикеры
POPULAR_TICKERS = {
    "🍎 AAPL": "AAPL",
    "🔍 GOOGL": "GOOGL",
    "🪟 MSFT": "MSFT",
    "⚡ TSLA": "TSLA",
    "📦 AMZN": "AMZN",
    "🎮 NVDA": "NVDA",
    "💰 META": "META",
    "🎬 NFLX": "NFLX",
    "💳 V": "V",
    "🏦 JPM": "JPM",
    "💊 JNJ": "JNJ",
    "🥤 KO": "KO",
    "🍔 MCD": "MCD",
    "✈️ BA": "BA",
    "🚗 F": "F",
    "💻 INTC": "INTC",
    "💎 AMD": "AMD",
    "☁️ CRM": "CRM",
    "🎵 SPOT": "SPOT",
    "🎮 EA": "EA",
    "🏪 WMT": "WMT"
}

def get_main_menu():
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Тикер"), KeyboardButton(text="💵 Сумма")],
            [KeyboardButton(text="📅 Горизонт прогноза")],
            [KeyboardButton(text="📈 Анализ"), KeyboardButton(text="🧪 Испытание реальностью")],
            [KeyboardButton(text="🔄 Перезапуск"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="📋 О боте")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие из меню"
    )
    return keyboard

def get_forecast_menu():
    """Меню выбора горизонта прогноза"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 5 дней"), KeyboardButton(text="📅 10 дней"), KeyboardButton(text="📅 15 дней")],
            [KeyboardButton(text="📅 20 дней"), KeyboardButton(text="📅 25 дней"), KeyboardButton(text="📅 30 дней")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_status_message(ticker=None, amount=None, forecast_days=30):
    """Сообщение со статусом выбора"""
    from datetime import datetime, timedelta
    
    ticker_text = ticker if ticker else "не выбрано"
    amount_text = f"${amount}" if amount else "не выбрано"
    
    # Рассчитываем период прогноза
    today = datetime.now()
    forecast_end = today + timedelta(days=forecast_days)
    period_text = f"{today.strftime('%d.%m.%Y')} - {forecast_end.strftime('%d.%m.%Y')}"
    
    return (
        f"📊 Тикер: {ticker_text}\n"
        f"💰 Сумма: {amount_text}\n"
        f"📅 Горизонт прогноза: {forecast_days} дней ({period_text})"
    )

def get_ticker_menu():
    """Меню выбора тикера"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍎 AAPL"), KeyboardButton(text="🔍 GOOGL"), KeyboardButton(text="🪟 MSFT")],
            [KeyboardButton(text="⚡ TSLA"), KeyboardButton(text="📦 AMZN"), KeyboardButton(text="🎮 NVDA")],
            [KeyboardButton(text="💰 META"), KeyboardButton(text="🎬 NFLX"), KeyboardButton(text="💳 V")],
            [KeyboardButton(text="🏦 JPM"), KeyboardButton(text="💊 JNJ"), KeyboardButton(text="🥤 KO")],
            [KeyboardButton(text="🍔 MCD"), KeyboardButton(text="✈️ BA"), KeyboardButton(text="🚗 F")],
            [KeyboardButton(text="💻 INTC"), KeyboardButton(text="💎 AMD"), KeyboardButton(text="☁️ CRM")],
            [KeyboardButton(text="🎵 SPOT"), KeyboardButton(text="🎮 EA"), KeyboardButton(text="🏪 WMT")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_amount_menu():
    """Меню выбора суммы инвестиций"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💵 100"), KeyboardButton(text="💵 200"), KeyboardButton(text="💵 500")],
            [KeyboardButton(text="💵 1000"), KeyboardButton(text="✏️ Своя")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_help_text():
    """Текст помощи"""
    return (
        "📖 **КАК ПОЛЬЗОВАТЬСЯ БОТОМ:**\n\n"
        "**🚀 Основной режим:**\n"
        "1. 🔍 Нажми 'Тикер' и выбери акцию\n"
        "2. 💵 Нажми 'Сумма' и выбери сумму инвестиции\n"
        "3. 📅 Выбери горизонт прогноза (5-30 дней)\n"
        "4. 📈 Нажми 'Анализ' для получения прогноза\n\n"
        "**🧪 Режим тестирования:**\n"
        "5. 🧪 'Испытание реальностью' - проверь точность прогнозов\n\n"
        "**🛠️ Дополнительные команды:**\n"
        "• /start - перезапуск бота\n"
        "• /debug - диагностика проблем\n"
        "• 🔄 Перезапуск - сброс настроек\n\n"
        "**💡 Если есть проблемы с загрузкой данных:**\n"
        "• Проверь правильность тикера\n"
        "• Попробуй другую акцию из списка\n"
        "• Используй /debug для проверки"
    )

def get_about_text():
    """Информация о боте"""
    return (
        "🤖 FinGolem Bot\n\n"
        "Бот для анализа финансовых данных\n"
        "Получает данные с Yahoo Finance\n"
        "Строит графики цен акций за 2 года"
    )

def get_reality_test_menu():
    """Меню для режима испытания реальностью"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔬 Создать тест"), KeyboardButton(text="� Мои тесты")],
            [KeyboardButton(text="📈 Выполнить готовые"), KeyboardButton(text="📊 Статус тестов")],
            [KeyboardButton(text="🗑️ Отменить тест")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_test_date_menu():
    """Меню для выбора даты тестирования"""
    from datetime import datetime, timedelta
    
    today = datetime.now()
    dates = []
    
    # Предлагаем даты на следующие дни
    for i in range(1, 8):  # 1-7 дней вперед
        date = today + timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"📅 {dates[0]}"), KeyboardButton(text=f"📅 {dates[1]}")],
            [KeyboardButton(text=f"📅 {dates[2]}"), KeyboardButton(text=f"📅 {dates[3]}")],
            [KeyboardButton(text=f"📅 {dates[4]}"), KeyboardButton(text=f"📅 {dates[5]}")],
            [KeyboardButton(text=f"📅 {dates[6]}"), KeyboardButton(text="✏️ Своя дата")],
            [KeyboardButton(text="◀️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_reality_test_help_text():
    """Текст помощи для режима испытания реальностью"""
    return (
        "🧪 **ИСПЫТАНИЕ РЕАЛЬНОСТЬЮ**\n\n"
        "Этот режим позволяет проверить точность прогнозов на реальных данных.\n\n"
        "📋 **Как это работает:**\n"
        "1. Создайте прогноз через обычный анализ\n"
        "2. Активируйте 'Испытание реальностью'\n"
        "3. Выберите дату для проверки прогноза\n"
        "4. В указанную дату бот автоматически:\n"
        "   • Загрузит актуальные котировки\n"
        "   • Сравнит их с прогнозом\n"
        "   • Покажет метрики точности\n\n"
        "📊 **Метрики оценки:**\n"
        "• RMSE - среднеквадратичная ошибка\n"
        "• MAPE - средняя абсолютная процентная ошибка\n"
        "• Точность направления - правильность предсказания тренда\n"
        "• Точность в пределах ±5% и ±10%\n\n"
        "💡 Используйте этот режим для оценки качества моделей прогнозирования!"
    )
