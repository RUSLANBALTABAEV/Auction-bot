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
    echo Попытка установки по отдельности...
    pip install playwright python-telegram-bot PyYAML aiohttp pytest pytest-asyncio pyinstaller
    pip install PyQt6 qasync
)

echo Установка браузера для Playwright...
playwright install chromium

echo Создание необходимых директорий...
if not exist screenshots mkdir screenshots
if not exist logs mkdir logs
if not exist configs mkdir configs
if not exist gui mkdir gui

echo Копирование конфигурационных файлов...
copy config.yaml configs\config_default.yaml >nul 2>&1

echo ========================================
echo    УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo Доступные режимы запуска:
echo   python main.py --gui-pyqt  - PyQt6 графический интерфейс
echo   python main.py --gui-tk    - Tkinter графический интерфейс  
echo   python main.py --edit-config - Консольный режим
echo   python main.py --help      - Справка
echo.
echo Установленные версии:
python -c "import PyQt6; print(f'PyQt6: {PyQt6.QtCore.QT_VERSION_STR}')" 2>nul || echo PyQt6: не установлен
python -c "import playwright; print(f'Playwright: {playwright.__version__}')" 2>nul || echo Playwright: не установлен
echo.
pause
