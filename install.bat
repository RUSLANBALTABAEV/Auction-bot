@echo off
chcp 65001
title Установка Auction Bot

echo ========================================
echo    УСТАНОВКА AUCTION BOT
echo ========================================

echo Проверка установки Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не установлен!
    echo Скачайте и установите Python 3.9+ с python.org
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements.txt

if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)

echo Установка браузера для Playwright...
playwright install chromium

echo Создание необходимых директорий...
if not exist screenshots mkdir screenshots
if not exist logs mkdir logs
if not exist configs mkdir configs

echo Копирование конфигурационных файлов...
copy config.yaml configs\config_default.yaml >nul 2>&1

echo ========================================
echo    УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo Доступные команды:
echo   python main.py --gui      - запуск с интерфейсом
echo   python main.py --help     - справка
echo   python run_bot.py default - быстрый запуск
echo.
pause
