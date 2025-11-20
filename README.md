# Auction Bot

Бот для автоматической подачи ставок на аукционах.

## Установка

1. Установите Python 3.9+
2. Установите зависимости:

pip install -r requirements.txt
playwright install

3. Настройте конфигурацию в `config.yaml`

## Запуск

### Консольный режим

python main.py


### Графический интерфейс

python main.py --gui


### С фоновым браузером

python main.py --headless


## Настройка NCALayer

Убедитесь, что NCALayer установлен и настроен на вашем компьютере.

## Тестирование

Запустите тесты:

pytest tests/

## Сборка в EXE

pyinstaller --onefile --windowed main.py

## Важно

Используйте бота только в разрешенных целях и в соответствии с правилами аукционных площадок.

13. Сборка в EXE

Создадим скрипт для сборки.

build.bat (для Windows)

@echo off

pyinstaller --onefile --windowed --name "AuctionBot" --add-data "config.yaml;." main.py

pause

build.sh (для Linux)

#!/bin/bash
pyinstaller --onefile --windowed --name "AuctionBot" --add-data "config.yaml:." main.py
