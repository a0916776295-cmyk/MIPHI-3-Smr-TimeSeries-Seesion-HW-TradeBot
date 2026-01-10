# -*- coding: utf-8 -*-
import sys
import os

# Настройка кодировки для Windows
if sys.platform.startswith('win'):
    # Устанавливаем UTF-8 для stdout и stderr
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

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

if __name__ == "__main__":
    safe_print("Тестируем кириллицу в консоли...")
    safe_print("Бот запущен и ожидает сообщения...")
    safe_print("Анализ данных завершен!")
    safe_print("Ошибка при обработке запроса")
    print("Обычный print")
    safe_print("🚀 Эмодзи тоже должны работать! 📈📊💰")