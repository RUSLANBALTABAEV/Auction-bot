"""
Генератор конфигурационных файлов
"""
import yaml
import os
from config_manager import ConfigManager


def generate_config():
    """Интерактивный генератор конфигурации"""
    print("🎯 Генератор конфигурации Auction Bot")
    print("=" * 50)
    
    config_manager = ConfigManager()
    
    try:
        # Аукцион
        print("\n📊 Настройки аукциона:")
        config_manager.config['auction']['url'] = input(f"URL аукциона [{config_manager.config['auction']['url']}]: ").strip() or config_manager.config['auction']['url']
        config_manager.config['auction']['price_limit'] = int(input(f"Лимит цены [{config_manager.config['auction']['price_limit']}]: ").strip() or config_manager.config['auction']['price_limit'])
        config_manager.config['auction']['bid_delay'] = int(input(f"Задержка подачи (мс) [{config_manager.config['auction']['bid_delay']}]: ").strip() or config_manager.config['auction']['bid_delay'])
        config_manager.config['auction']['refresh_interval'] = int(input(f"Интервал проверки (мс) [{config_manager.config['auction']['refresh_interval']}]: ").strip() or config_manager.config['auction']['refresh_interval'])
        
        # Селекторы
        print("\n🎯 Селекторы:")
        selectors = config_manager.config['auction']['selectors']
        selectors['bid_button'] = input(f"Селектор кнопки ставки [{selectors['bid_button']}]: ").strip() or selectors['bid_button']
        selectors['timer'] = input(f"Селектор таймера [{selectors['timer']}]: ").strip() or selectors['timer']
        selectors['status'] = input(f"Селектор статуса [{selectors['status']}]: ").strip() or selectors['status']
        selectors['sign_data'] = input(f"Селектор данных для подписи [{selectors['sign_data']}]: ").strip() or selectors['sign_data']
        selectors['signature_input'] = input(f"Селектор поля подписи [{selectors['signature_input']}]: ").strip() or selectors['signature_input']
        
        # NCALayer
        print("\n🔐 Настройки NCALayer:")
        config_manager.config['ncalayer']['port'] = int(input(f"Порт NCALayer [{config_manager.config['ncalayer']['port']}]: ").strip() or config_manager.config['ncalayer']['port'])
        config_manager.config['ncalayer']['storage'] = input(f"Тип хранилища (PKCS12/PKCS8) [{config_manager.config['ncalayer']['storage']}]: ").strip() or config_manager.config['ncalayer']['storage']
        config_manager.config['ncalayer']['password'] = input(f"Пароль хранилища [{config_manager.config['ncalayer']['password']}]: ").strip() or config_manager.config['ncalayer']['password']
        
        # Telegram
        print("\n📱 Настройки Telegram:")
        telegram_enabled = input(f"Включить Telegram уведомления (y/n) [{'y' if config_manager.config['telegram']['enabled'] else 'n'}]: ").strip().lower()
        if telegram_enabled:
            config_manager.config['telegram']['enabled'] = telegram_enabled == 'y'
            
        if config_manager.config['telegram']['enabled'] or telegram_enabled == 'y':
            config_manager.config['telegram']['bot_token'] = input(f"Token бота Telegram [{config_manager.config['telegram']['bot_token']}]: ").strip() or config_manager.config['telegram']['bot_token']
            config_manager.config['telegram']['chat_id'] = input(f"Chat ID пользователя [{config_manager.config['telegram']['chat_id']}]: ").strip() or config_manager.config['telegram']['chat_id']
        
        # Логирование
        print("\n📝 Настройки логирования:")
        screenshots_enabled = input(f"Сохранять скриншоты (y/n) [{'y' if config_manager.config['logging']['screenshots'] else 'n'}]: ").strip().lower()
        if screenshots_enabled:
            config_manager.config['logging']['screenshots'] = screenshots_enabled == 'y'
        
        profile_name = input("\n💾 Имя профиля [default]: ").strip() or "default"
        filename = f"config_{profile_name}.yaml"
        
        if config_manager.save_config(filename):
            print(f"✅ Конфигурация сохранена в {filename}")
            print("Для запуска используйте:")
            print(f"  python main.py --config {filename}")
        else:
            print("❌ Ошибка сохранения конфигурации")
                
    except KeyboardInterrupt:
        print("\n❌ Генерация отменена")
    except Exception as e:
        print(f"❌ Ошибка при генерации: {e}")


if __name__ == "__main__":
    generate_config()
