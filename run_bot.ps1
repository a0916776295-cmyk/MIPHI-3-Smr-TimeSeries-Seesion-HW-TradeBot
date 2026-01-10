# Скрипт для запуска бота с правильной кодировкой
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
chcp 65001 | Out-Null

Write-Host "Запуск Telegram бота с поддержкой кириллицы..." -ForegroundColor Green
python FinGolem.py