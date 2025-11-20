"""
Генератор конфигурационных файлов
"""
import yaml
import os


def generate_config():
    """Интерактивный генератор конфигурации"""
    print("🎯 Генератор конфигурации Auction Bot")
    print("=" * 50)
    
    config = {
        'auction': {
            'url': input("URL аукциона: ").strip() or "https://auction-site.com/lot/123",
            'price_limit': int(input("Лимит цены: ").strip() or "1000000"),
            'bid_delay': int(input("Задержка подачи (мс): ").strip() or "100"),
            'refresh_interval': int(input("Интервал проверки (мс): ").strip() or "200"),
            'selectors': {
                'bid_button': input("Селектор кнопки ставки: ").strip() or "button.bid-button:not([disabled])",
                'timer': input("Селектор таймера: ").strip() or ".auction-timer",
                'status': input("Селектор статуса: ").strip() or ".auction-status",
                'sign_data': input("Селектор данных для подписи: ").strip() or "#signData",
                'signature_input': input("Селектор поля подписи: ").strip() or "#signatureInput"
            }
        },
        'ncalayer': {
            'port': int(input("Порт NCALayer: ").strip() or "13579"),
            'storage': input("Тип хранилища (PKCS12/PKCS8): ").strip() or "PKCS12",
            'password': input("Пароль хранилища: ").strip() or "",
            'timeout': 30000
        },
        'telegram': {
            'enabled': input("Включить Telegram уведомления (y/n): ").strip().lower() == 'y',
            'bot_token': input("Token бота Telegram: ").strip() or "YOUR_BOT_TOKEN",
            'chat_id': input("Chat ID: ").strip() or "YOUR_CHAT_ID"
        },
        'logging': {
            'level': input("Уровень логирования (INFO/DEBUG): ").strip() or "INFO",
            'screenshots': input("Сохранять скриншоты (y/n): ").strip().lower() == 'y',
            'screenshots_path': "screenshots",
            'log_file': "auction_bot.log",
            'max_log_size': 10485760
        },
        'browser': {
            'headless': False,
            'timeout': 30000,
            'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }
    
    profile_name = input("Имя профиля: ").strip() or "default"
    filename = f"config_{profile_name}.yaml"
    
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print(f"\n✅ Конфигурация сохранена в {filename}")
    print("Для запуска используйте:")
    print(f"  python run_bot.py {profile_name}")


if __name__ == "__main__":
    generate_config()
