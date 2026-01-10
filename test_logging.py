# -*- coding: utf-8 -*-
"""
Тест логирования бота
"""

import sys
import os

# Настройка кодировки для Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def safe_print(text):
    """Безопасный вывод текста с поддержкой кириллицы"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print("Output encoding error")

def test_bot_imports():
    """Тестируем импорт бота с новым логированием"""
    safe_print("🧪 Тестирование импортов бота с логированием...")
    
    try:
        # Проверяем импорт основных модулей
        import FinGolem
        safe_print("✅ FinGolem импортирован успешно")
        
        # Проверяем функции логирования
        from FinGolem import safe_print as bot_safe_print
        bot_safe_print("✅ Функция safe_print работает")
        
        # Проверяем импорт datetime
        from datetime import datetime
        safe_print(f"✅ datetime импортирован: {datetime.now().strftime('%H:%M:%S')}")
        
        safe_print("🎉 Все компоненты готовы к работе!")
        
    except Exception as e:
        safe_print(f"❌ Ошибка импорта: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    safe_print("🚀 Тестирование системы логирования")
    safe_print("=" * 40)
    test_bot_imports()
    safe_print("=" * 40)
    safe_print("🏁 Тестирование завершено!")