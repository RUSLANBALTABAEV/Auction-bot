import sys
import os
import yaml
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QLineEdit, QSpinBox, QCheckBox, 
                             QPushButton, QTextEdit, QMessageBox, QTabWidget,
                             QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt

class ConfigEditor(QMainWindow):
    def __init__(self, config_path="config.yaml"):
        super().__init__()
        self.config_path = config_path
        self.config = {}
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("Редактор конфигурации Auction Bot")
        self.setGeometry(100, 100, 600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Создаем вкладки
        tabs = QTabWidget()
        tabs.addTab(self.create_auction_tab(), "Аукцион")
        tabs.addTab(self.create_ncalayer_tab(), "NCALayer")
        tabs.addTab(self.create_telegram_tab(), "Telegram")
        tabs.addTab(self.create_logging_tab(), "Логирование")
        tabs.addTab(self.create_browser_tab(), "Браузер")

        layout.addWidget(tabs)

        # Кнопки сохранения и загрузки
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.load_btn = QPushButton("Загрузить")
        self.exit_btn = QPushButton("Выход")

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.load_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.exit_btn)

        layout.addLayout(buttons_layout)

        central_widget.setLayout(layout)

        # Подключаем кнопки
        self.save_btn.clicked.connect(self.save_config)
        self.load_btn.clicked.connect(self.load_config)
        self.exit_btn.clicked.connect(self.close)

    def create_auction_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.auction_url = QLineEdit()
        layout.addRow("URL аукциона:", self.auction_url)

        self.price_limit = QSpinBox()
        self.price_limit.setRange(0, 1000000000)
        layout.addRow("Лимит цены:", self.price_limit)

        self.bid_delay = QSpinBox()
        self.bid_delay.setRange(0, 5000)
        self.bid_delay.setSuffix(" мс")
        layout.addRow("Задержка подачи:", self.bid_delay)

        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(50, 5000)
        self.refresh_interval.setSuffix(" мс")
        layout.addRow("Интервал проверки:", self.refresh_interval)

        # Группа для селекторов
        selectors_group = QGroupBox("Селекторы")
        selectors_layout = QFormLayout()

        self.bid_button_selector = QLineEdit()
        selectors_layout.addRow("Кнопка ставки:", self.bid_button_selector)

        self.timer_selector = QLineEdit()
        selectors_layout.addRow("Таймер:", self.timer_selector)

        self.status_selector = QLineEdit()
        selectors_layout.addRow("Статус:", self.status_selector)

        self.sign_data_selector = QLineEdit()
        selectors_layout.addRow("Данные для подписи:", self.sign_data_selector)

        self.signature_input_selector = QLineEdit()
        selectors_layout.addRow("Поле подписи:", self.signature_input_selector)

        selectors_group.setLayout(selectors_layout)
        layout.addRow(selectors_group)

        tab.setLayout(layout)
        return tab

    def create_ncalayer_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.ncalayer_port = QSpinBox()
        self.ncalayer_port.setRange(1, 65535)
        layout.addRow("Порт NCALayer:", self.ncalayer_port)

        self.storage_type = QLineEdit()
        layout.addRow("Тип хранилища:", self.storage_type)

        self.storage_password = QLineEdit()
        self.storage_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль хранилища:", self.storage_password)

        tab.setLayout(layout)
        return tab

    def create_telegram_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.telegram_enabled = QCheckBox()
        layout.addRow("Включить уведомления:", self.telegram_enabled)

        self.telegram_bot_token = QLineEdit()
        layout.addRow("Token бота:", self.telegram_bot_token)

        self.telegram_chat_id = QLineEdit()
        layout.addRow("Chat ID:", self.telegram_chat_id)

        tab.setLayout(layout)
        return tab

    def create_logging_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.screenshots_enabled = QCheckBox()
        layout.addRow("Сохранять скриншоты:", self.screenshots_enabled)

        tab.setLayout(layout)
        return tab

    def create_browser_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.headless = QCheckBox()
        layout.addRow(" headless режим:", self.headless)

        tab.setLayout(layout)
        return tab

    def load_config(self):
        """Загрузка конфигурации из файла"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                self.update_ui_from_config()
                QMessageBox.information(self, "Успех", "Конфигурация загружена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить конфигурацию: {e}")
        else:
            QMessageBox.information(self, "Информация", "Конфигурационный файл не найден. Заполните поля и нажмите 'Сохранить'.")

    def update_ui_from_config(self):
        """Обновление UI из загруженной конфигурации"""
        # Аукцион
        auction = self.config.get('auction', {})
        self.auction_url.setText(auction.get('url', ''))
        self.price_limit.setValue(auction.get('price_limit', 0))
        self.bid_delay.setValue(auction.get('bid_delay', 100))
        self.refresh_interval.setValue(auction.get('refresh_interval', 200))

        selectors = auction.get('selectors', {})
        self.bid_button_selector.setText(selectors.get('bid_button', ''))
        self.timer_selector.setText(selectors.get('timer', ''))
        self.status_selector.setText(selectors.get('status', ''))
        self.sign_data_selector.setText(selectors.get('sign_data', ''))
        self.signature_input_selector.setText(selectors.get('signature_input', ''))

        # NCALayer
        ncalayer = self.config.get('ncalayer', {})
        self.ncalayer_port.setValue(ncalayer.get('port', 13579))
        self.storage_type.setText(ncalayer.get('storage', 'PKCS12'))
        self.storage_password.setText(ncalayer.get('password', ''))

        # Telegram
        telegram = self.config.get('telegram', {})
        self.telegram_enabled.setChecked(telegram.get('enabled', False))
        self.telegram_bot_token.setText(telegram.get('bot_token', ''))
        self.telegram_chat_id.setText(telegram.get('chat_id', ''))

        # Логирование
        logging = self.config.get('logging', {})
        self.screenshots_enabled.setChecked(logging.get('screenshots', True))

        # Браузер
        browser = self.config.get('browser', {})
        self.headless.setChecked(browser.get('headless', False))

    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            self.config = {
                'auction': {
                    'url': self.auction_url.text(),
                    'price_limit': self.price_limit.value(),
                    'bid_delay': self.bid_delay.value(),
                    'refresh_interval': self.refresh_interval.value(),
                    'selectors': {
                        'bid_button': self.bid_button_selector.text(),
                        'timer': self.timer_selector.text(),
                        'status': self.status_selector.text(),
                        'sign_data': self.sign_data_selector.text(),
                        'signature_input': self.signature_input_selector.text()
                    }
                },
                'ncalayer': {
                    'port': self.ncalayer_port.value(),
                    'storage': self.storage_type.text(),
                    'password': self.storage_password.text(),
                    'timeout': 30000
                },
                'telegram': {
                    'enabled': self.telegram_enabled.isChecked(),
                    'bot_token': self.telegram_bot_token.text(),
                    'chat_id': self.telegram_chat_id.text()
                },
                'logging': {
                    'level': 'INFO',
                    'screenshots': self.screenshots_enabled.isChecked(),
                    'screenshots_path': 'screenshots',
                    'log_file': 'auction_bot.log',
                    'max_log_size': 10485760
                },
                'browser': {
                    'headless': self.headless.isChecked(),
                    'timeout': 30000,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)

            QMessageBox.information(self, "Успех", "Конфигурация сохранена!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфигурацию: {e}")


def main():
    app = QApplication(sys.argv)
    editor = ConfigEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
