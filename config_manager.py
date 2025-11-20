"""
Универсальный менеджер конфигурации
"""
import yaml
import os
from typing import Dict, Any


class ConfigManager:
    """Класс для управления конфигурацией"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_default_config()
        self.load_config()
    
    def load_default_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации по умолчанию"""
        return {
            'auction': {
                'url': "https://auction-site.com/lot/123",
                'price_limit': 1000000,
                'bid_delay': 100,
                'refresh_interval': 200,
                'selectors': {
                    'bid_button': "button.bid-button:not([disabled])",
                    'timer': ".auction-timer", 
                    'status': ".auction-status",
                    'sign_data': "#signData",
                    'signature_input': "#signatureInput"
                }
            },
            'ncalayer': {
                'port': 13579,
                'storage': "PKCS12",
                'password': "",
                'timeout': 30000
            },
            'telegram': {
                'enabled': False,
                'bot_token': "YOUR_BOT_TOKEN",
                'chat_id': "YOUR_CHAT_ID"
            },
            'logging': {
                'level': "INFO",
                'screenshots': True,
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
    
    def load_config(self) -> bool:
        """Загрузка конфигурации из файла"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f) or {}
                    self._deep_update(self.config, loaded_config)
                print(f"✅ Конфигурация загружена из {self.config_path}")
                return True
            else:
                print(f"⚠️ Файл {self.config_path} не найден, используются настройки по умолчанию")
                return False
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            return False
    
    def save_config(self, path: str = None) -> bool:
        """Сохранение конфигурации в файл"""
        save_path = path or self.config_path
        try:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
            print(f"✅ Конфигурация сохранена в {save_path}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
            return False
    
    def apply_command_line_args(self, args) -> bool:
        """Применение параметров из командной строки"""
        changes_made = False
        
        # Параметры аукциона
        if args.url:
            self.config['auction']['url'] = args.url
            changes_made = True
            
        if args.price_limit:
            self.config['auction']['price_limit'] = args.price_limit
            changes_made = True
            
        if args.bid_delay:
            self.config['auction']['bid_delay'] = args.bid_delay
            changes_made = True
            
        if args.refresh_interval:
            self.config['auction']['refresh_interval'] = args.refresh_interval
            changes_made = True
        
        # Селекторы
        if args.bid_button_selector:
            self.config['auction']['selectors']['bid_button'] = args.bid_button_selector
            changes_made = True
            
        if args.timer_selector:
            self.config['auction']['selectors']['timer'] = args.timer_selector
            changes_made = True
            
        if args.status_selector:
            self.config['auction']['selectors']['status'] = args.status_selector
            changes_made = True
            
        if args.sign_data_selector:
            self.config['auction']['selectors']['sign_data'] = args.sign_data_selector
            changes_made = True
            
        if args.signature_input_selector:
            self.config['auction']['selectors']['signature_input'] = args.signature_input_selector
            changes_made = True
        
        # NCALayer
        if args.ncalayer_port:
            self.config['ncalayer']['port'] = args.ncalayer_port
            changes_made = True
            
        if args.storage_type:
            self.config['ncalayer']['storage'] = args.storage_type
            changes_made = True
            
        if args.storage_password:
            self.config['ncalayer']['password'] = args.storage_password
            changes_made = True
        
        # Telegram
        if args.telegram_token:
            self.config['telegram']['bot_token'] = args.telegram_token
            changes_made = True
            
        if args.chat_id:
            self.config['telegram']['chat_id'] = args.chat_id
            changes_made = True
            
        if args.enable_telegram:
            self.config['telegram']['enabled'] = True
            changes_made = True
            
        if args.disable_telegram:
            self.config['telegram']['enabled'] = False
            changes_made = True
        
        # Логирование
        if args.enable_screenshots:
            self.config['logging']['screenshots'] = True
            changes_made = True
            
        if args.disable_screenshots:
            self.config['logging']['screenshots'] = False
            changes_made = True
        
        return changes_made
    
    def interactive_config_edit(self) -> bool:
        """Интерактивное редактирование конфигурации в консоли"""
        print("\n🎯 Редактирование конфигурации")
        print("=" * 50)
        
        try:
            # Аукцион
            print("\n📊 Настройки аукциона:")
            self.config['auction']['url'] = input(f"URL аукциона [{self.config['auction']['url']}]: ").strip() or self.config['auction']['url']
            self.config['auction']['price_limit'] = int(input(f"Лимит цены [{self.config['auction']['price_limit']}]: ").strip() or self.config['auction']['price_limit'])
            self.config['auction']['bid_delay'] = int(input(f"Задержка подачи (мс) [{self.config['auction']['bid_delay']}]: ").strip() or self.config['auction']['bid_delay'])
            self.config['auction']['refresh_interval'] = int(input(f"Интервал проверки (мс) [{self.config['auction']['refresh_interval']}]: ").strip() or self.config['auction']['refresh_interval'])
            
            # Селекторы
            print("\n🎯 Селекторы:")
            selectors = self.config['auction']['selectors']
            selectors['bid_button'] = input(f"Селектор кнопки ставки [{selectors['bid_button']}]: ").strip() or selectors['bid_button']
            selectors['timer'] = input(f"Селектор таймера [{selectors['timer']}]: ").strip() or selectors['timer']
            selectors['status'] = input(f"Селектор статуса [{selectors['status']}]: ").strip() or selectors['status']
            selectors['sign_data'] = input(f"Селектор данных для подписи [{selectors['sign_data']}]: ").strip() or selectors['sign_data']
            selectors['signature_input'] = input(f"Селектор поля подписи [{selectors['signature_input']}]: ").strip() or selectors['signature_input']
            
            # NCALayer
            print("\n🔐 Настройки NCALayer:")
            self.config['ncalayer']['port'] = int(input(f"Порт NCALayer [{self.config['ncalayer']['port']}]: ").strip() or self.config['ncalayer']['port'])
            self.config['ncalayer']['storage'] = input(f"Тип хранилища (PKCS12/PKCS8) [{self.config['ncalayer']['storage']}]: ").strip() or self.config['ncalayer']['storage']
            self.config['ncalayer']['password'] = input(f"Пароль хранилища [{self.config['ncalayer']['password']}]: ").strip() or self.config['ncalayer']['password']
            
            # Telegram
            print("\n📱 Настройки Telegram:")
            telegram_enabled = input(f"Включить Telegram уведомления (y/n) [{'y' if self.config['telegram']['enabled'] else 'n'}]: ").strip().lower()
            if telegram_enabled:
                self.config['telegram']['enabled'] = telegram_enabled == 'y'
                
            if self.config['telegram']['enabled'] or telegram_enabled == 'y':
                self.config['telegram']['bot_token'] = input(f"Token бота Telegram [{self.config['telegram']['bot_token']}]: ").strip() or self.config['telegram']['bot_token']
                self.config['telegram']['chat_id'] = input(f"Chat ID пользователя [{self.config['telegram']['chat_id']}]: ").strip() or self.config['telegram']['chat_id']
            
            # Логирование
            print("\n📝 Настройки логирования:")
            screenshots_enabled = input(f"Сохранять скриншоты (y/n) [{'y' if self.config['logging']['screenshots'] else 'n'}]: ").strip().lower()
            if screenshots_enabled:
                self.config['logging']['screenshots'] = screenshots_enabled == 'y'
            
            # Сохранение
            save = input("\n💾 Сохранить конфигурацию? (y/n) [y]: ").strip().lower() or 'y'
            if save == 'y':
                return self.save_config()
            else:
                print("❌ Изменения не сохранены")
                return False
                
        except KeyboardInterrupt:
            print("\n❌ Редактирование отменено")
            return False
        except Exception as e:
            print(f"❌ Ошибка при редактировании: {e}")
            return False
    
    def get_config_summary(self) -> str:
        """Получение краткой информации о конфигурации"""
        return f"""
📋 Конфигурация ({self.config_path}):

Аукцион:
  URL: {self.config['auction']['url']}
  Лимит цены: {self.config['auction']['price_limit']:,}
  Задержка: {self.config['auction']['bid_delay']} мс
  Интервал проверки: {self.config['auction']['refresh_interval']} мс

NCALayer:
  Порт: {self.config['ncalayer']['port']}
  Хранилище: {self.config['ncalayer']['storage']}

Telegram: {'✅ Включен' if self.config['telegram']['enabled'] else '❌ Выключен'}
Скриншоты: {'✅ Включены' if self.config['logging']['screenshots'] else '❌ Выключены'}
        """.strip()
    
    @classmethod
    def generate_config_interactive(cls, profile_name: str = "default"):
        """Генерация новой конфигурации"""
        config_manager = cls(f"config_{profile_name}.yaml")
        if config_manager.interactive_config_edit():
            print(f"✅ Конфигурационный файл создан: config_{profile_name}.yaml")
    
    @classmethod
    def list_profiles(cls):
        """Показать все профили конфигурации"""
        config_files = [f for f in os.listdir('.') if f.startswith('config_') and f.endswith('.yaml')]
        if config_files:
            print("\n📁 Доступные профили конфигурации:")
            for config_file in config_files:
                profile_name = config_file[7:-5]  # Убираем 'config_' и '.yaml'
                print(f"  - {profile_name} ({config_file})")
        else:
            print("❌ Профили конфигурации не найдены")
    
    def _deep_update(self, original: Dict, update: Dict):
        """Рекурсивное обновление словаря"""
        for key, value in update.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                self._deep_update(original[key], value)
            else:
                original[key] = value
    
    def __getitem__(self, key):
        """Доступ к конфигурации как к словарю"""
        return self.config[key]
    
    def get(self, key, default=None):
        """Безопасный доступ к конфигурации"""
        return self.config.get(key, default)


if __name__ == "__main__":
    config = ConfigManager()
    print(config.get_config_summary())
