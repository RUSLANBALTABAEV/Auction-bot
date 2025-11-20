#!/usr/bin/env python3
"""
Главный запускаемый файл Auction Bot с поддержкой всех режимов
"""
import asyncio
import argparse
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Auction Bot - Бот для быстрой подачи ставки на аукционе',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  Консольный режим:
    python main.py --url "https://auction.com/lot/123" --price-limit 1000000
    python main.py --edit-config

  Графический режим PyQt6:
    python main.py --gui-pyqt

  Графический режим Tkinter:
    python main.py --gui-tk

  Тестирование:
    python main.py --test-speed 5
        """
    )
    
    # Режимы запуска
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--gui-pyqt', action='store_true', help='Запуск с графическим интерфейсом PyQt6')
    mode_group.add_argument('--gui-tk', action='store_true', help='Запуск с графическим интерфейсом Tkinter')
    
    # Основные параметры
    parser.add_argument('--config', default='config.yaml', help='Путь к конфигурационному файлу')
    parser.add_argument('--headless', action='store_true', help='Запуск браузера в фоновом режиме')
    parser.add_argument('--edit-config', action='store_true', help='Редактировать конфигурацию перед запуском')
    
    # Параметры аукциона
    parser.add_argument('--url', help='URL аукциона')
    parser.add_argument('--price-limit', type=int, help='Лимит цены')
    parser.add_argument('--bid-delay', type=int, help='Задержка подачи (мс)')
    parser.add_argument('--refresh-interval', type=int, help='Интервал проверки (мс)')
    
    # Селекторы
    parser.add_argument('--bid-button-selector', help='Селектор кнопки ставки')
    parser.add_argument('--timer-selector', help='Селектор таймера') 
    parser.add_argument('--status-selector', help='Селектор статуса')
    parser.add_argument('--sign-data-selector', help='Селектор данных для подписи')
    parser.add_argument('--signature-input-selector', help='Селектор поля подписи')
    
    # NCALayer
    parser.add_argument('--ncalayer-port', type=int, help='Порт NCALayer')
    parser.add_argument('--storage-type', help='Тип хранилища (PKCS12/PKCS8)')
    parser.add_argument('--storage-password', help='Пароль хранилища')
    
    # Telegram
    parser.add_argument('--telegram-token', help='Token бота Telegram')
    parser.add_argument('--chat-id', help='Chat ID пользователя Telegram')
    parser.add_argument('--enable-telegram', action='store_true', help='Включить Telegram уведомления')
    parser.add_argument('--disable-telegram', action='store_true', help='Выключить Telegram уведомления')
    
    # Логирование
    parser.add_argument('--enable-screenshots', action='store_true', help='Включить сохранение скриншотов')
    parser.add_argument('--disable-screenshots', action='store_true', help='Выключить сохранение скриншотов')
    
    # Дополнительные команды
    parser.add_argument('--generate-config', help='Сгенерировать конфигурационный файл с указанным именем')
    parser.add_argument('--list-profiles', action='store_true', help='Показать все профили конфигурации')
    parser.add_argument('--test-speed', type=int, help='Запустить тест скорости (количество попыток)')
    
    return parser.parse_args()


async def run_console_bot(args):
    """Запуск бота в консольном режиме"""
    try:
        config_manager = ConfigManager(args.config)
        
        # Применяем параметры из командной строки к конфигурации
        if config_manager.apply_command_line_args(args):
            print("✅ Параметры из командной строки применены")
        
        # Редактирование конфигурации если запрошено
        if args.edit_config:
            if not config_manager.interactive_config_edit():
                print("Редактирование отменено")
                return
        
        from bot.auction_bot import AuctionBot
        bot = AuctionBot(config_manager)
        if args.headless:
            bot.config['browser']['headless'] = True
            
        print("🚀 Запуск мониторинга аукциона...")
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n⏹ Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


def handle_special_commands(args):
    """Обработка специальных команд"""
    if args.generate_config:
        from config_manager import ConfigManager
        ConfigManager.generate_config_interactive(args.generate_config)
        return True
        
    if args.list_profiles:
        from config_manager import ConfigManager
        ConfigManager.list_profiles()
        return True
        
    if args.test_speed:
        from speed_test import SpeedTester
        tester = SpeedTester(args.config, args.test_speed)
        asyncio.run(tester.run_speed_test())
        return True
        
    return False


def run_pyqt6_gui(args):
    """Запуск PyQt6 графического интерфейса"""
    try:
        from gui.pyqt_gui import run_pyqt6_gui
        run_pyqt6_gui(args)
    except ImportError as e:
        print(f"❌ Не удалось запустить PyQt6 графический интерфейс: {e}")
        print("\n🔧 Решение: Установите PyQt6 или используйте другой режим")
        print("Установка: pip install PyQt6")
        print("Альтернативы:")
        print("  python main.py --gui-tk     # Tkinter GUI")
        print("  python main.py --edit-config # Консольный режим")
        sys.exit(1)


def run_tkinter_gui(args):
    """Запуск Tkinter графического интерфейса"""
    try:
        from gui.tkinter_gui import run_tkinter_gui
        run_tkinter_gui(args)
    except ImportError as e:
        print(f"❌ Не удалось запустить Tkinter графический интерфейс: {e}")
        print("Используйте консольный режим: python main.py --edit-config")
        sys.exit(1)


def main():
    """Основная функция запуска"""
    args = parse_arguments()
    
    # Обработка специальных команд
    if handle_special_commands(args):
        return
    
    # Выбор режима запуска
    if args.gui_pyqt:
        print("Запуск с графическим интерфейсом PyQt6...")
        run_pyqt6_gui(args)
    elif args.gui_tk:
        print("Запуск с графическим интерфейсом Tkinter...")
        run_tkinter_gui(args)
    else:
        print("Запуск в консольном режиме...")
        asyncio.run(run_console_bot(args))


if __name__ == "__main__":
    main()
