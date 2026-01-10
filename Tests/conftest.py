# -*- coding: utf-8 -*-
"""
Базовая конфигурация для тестов
"""

import os
import sys

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Путь к тестовым данным
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

# Создаем папку для тестовых данных если её нет
os.makedirs(TEST_DATA_DIR, exist_ok=True)