#!/usr/bin/env python3
"""
Главный запускаемый файл Auction Bot
"""
import asyncio
import argparse
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.auction_bot import AuctionBot
from gui.main_window import run_gui


def main():
    """Основная функция запуска"""
    parser = argparse.ArgumentParser(description='Auction Bot - Бот для быстрой подачи ставки на аукционе')
    parser.add_argument('--gui', action='store_true', help='Запуск с графическим интерфейсом')
    parser.add_argument('--config', default='config.yaml', help='Путь к конфигурационному файлу')
    parser.add_argument('--headless', action='store_true', help='Запуск браузера в фоновом режиме')
    
    args = parser.parse_args()
    
    if args.gui:
        print("Запуск с графическим интерфейсом...")
        run_gui()
    else:
        print("Запуск в консольном режиме...")
        asyncio.run(run_console_bot(args))


async def run_console_bot(args):
    """Запуск бота в консольном режиме"""
    try:
        bot = AuctionBot(args.config)
        if args.headless:
            bot.config['browser']['headless'] = True
            
        await bot.start_monitoring()
    except KeyboardInterrupt:
        print("\nОстановка бота...")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
