"""
Скрипт для быстрого запуска бота с разными профилями
"""
import asyncio
import sys
import os
from bot.auction_bot import AuctionBot


async def run_bot_profile(profile_name):
    """Запуск бота с определенным профилем"""
    config_file = f"config_{profile_name}.yaml"
    
    if not os.path.exists(config_file):
        print(f"Конфигурационный файл {config_file} не найден!")
        return
    
    print(f"Запуск бота с профилем: {profile_name}")
    
    try:
        bot = AuctionBot(config_file)
        await bot.start_monitoring()
    except KeyboardInterrupt:
        print("\nОстановка по команде пользователя")
    except Exception as e:
        print(f"Ошибка: {e}")


def main():
    """Основная функция"""
    if len(sys.argv) > 1:
        profile = sys.argv[1]
    else:
        profile = "default"
    
    asyncio.run(run_bot_profile(profile))


if __name__ == "__main__":
    main()
