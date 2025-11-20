"""
Графический интерфейс на PyQt6 для Auction Bot
"""
import sys
import os
import threading
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QPushButton, QTextEdit, QLabel, QTabWidget,
                           QLineEdit, QSpinBox, QCheckBox, QFormLayout, QGroupBox,
                           QMessageBox, QFileDialog, QComboBox, QProgressBar)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor
import qasync

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import ConfigManager


class BotThread(QThread):
    """Поток для запуска бота"""
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.bot = None
        self.is_running = True
    
    def run(self):
        """Запуск бота в отдельном потоке"""
        async def run_bot():
            try:
                from bot.auction_bot import AuctionBot
                self.bot = AuctionBot(self.config_manager)
                self.log_signal.emit("🚀 Запуск мониторинга аукциона...")
                await self.bot.start_monitoring()
            except Exception as e:
                self.log_signal.emit(f"❌ Ошибка: {e}")
            finally:
                self.finished_signal.emit()
        
        # Запускаем асинхронную функцию в потоке
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_bot())
        finally:
            loop.close()
    
    def stop(self):
        """Остановка бота"""
        self.is_running = False
        if self.bot:
            asyncio.run(self.bot.stop_monitoring())


class ConfigTab(QWidget):
    """Вкладка с настройками конфигурации"""
    
    def __init__(self, config_manager, log_callback):
        super().__init__()
        self.config_manager = config_manager
        self.log_callback = log_callback
        self.init_ui()
        self.load_current_config()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Вкладки настроек
        tabs = QTabWidget()
        
        # Вкладка аукциона
        auction_tab = self.create_auction_tab()
        tabs.addTab(auction_tab, "Аукцион")
        
        # Вкладка NCALayer
        ncalayer_tab = self.create_ncalayer_tab()
        tabs.addTab(ncalayer_tab, "NCALayer")
        
        # Вкладка Telegram
        telegram_tab = self.create_telegram_tab()
        tabs.addTab(telegram_tab, "Telegram")
        
        # Вкладка логирования
        logging_tab = self.create_logging_tab()
        tabs.addTab(logging_tab, "Логирование")
        
        layout.addWidget(tabs)
        
        # Кнопки управления конфигурацией
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 Сохранить")
        self.load_btn = QPushButton("📂 Загрузить")
        self.reset_btn = QPushButton("🔄 Сбросить")
        self.apply_btn = QPushButton("✅ Применить")
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.load_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addWidget(self.apply_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Подключаем сигналы
        self.save_btn.clicked.connect(self.save_config)
        self.load_btn.clicked.connect(self.load_config)
        self.reset_btn.clicked.connect(self.reset_config)
        self.apply_btn.clicked.connect(self.apply_config)
    
    def create_auction_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        # Основные параметры
        self.auction_url = QLineEdit()
        layout.addRow("URL аукциона:", self.auction_url)
        
        self.price_limit = QSpinBox()
        self.price_limit.setRange(0, 1000000000)
        self.price_limit.setSingleStep(1000)
        layout.addRow("Лимит цены:", self.price_limit)
        
        self.bid_delay = QSpinBox()
        self.bid_delay.setRange(0, 5000)
        self.bid_delay.setSuffix(" мс")
        self.bid_delay.setSingleStep(50)
        layout.addRow("Задержка подачи:", self.bid_delay)
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(50, 5000)
        self.refresh_interval.setSuffix(" мс")
        self.refresh_interval.setSingleStep(50)
        layout.addRow("Интервал проверки:", self.refresh_interval)
        
        # Группа селекторов
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
        
        self.storage_type = QComboBox()
        self.storage_type.addItems(["PKCS12", "PKCS8"])
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
        
        self.telegram_token = QLineEdit()
        layout.addRow("Token бота:", self.telegram_token)
        
        self.chat_id = QLineEdit()
        layout.addRow("Chat ID:", self.chat_id)
        
        # Информация о настройке Telegram
        info_label = QLabel(
            "Для настройки Telegram:\n"
            "1. Создайте бота через @BotFather\n"
            "2. Получите token\n" 
            "3. Узнайте ваш chat ID через @userinfobot"
        )
        info_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        layout.addRow(info_label)
        
        tab.setLayout(layout)
        return tab
    
    def create_logging_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        
        self.screenshots_enabled = QCheckBox()
        layout.addRow("Сохранять скриншоты:", self.screenshots_enabled)
        
        tab.setLayout(layout)
        return tab
    
    def load_current_config(self):
        """Загрузка текущей конфигурации в форму"""
        config = self.config_manager.config
        
        # Аукцион
        self.auction_url.setText(config['auction']['url'])
        self.price_limit.setValue(config['auction']['price_limit'])
        self.bid_delay.setValue(config['auction']['bid_delay'])
        self.refresh_interval.setValue(config['auction']['refresh_interval'])
        
        # Селекторы
        selectors = config['auction']['selectors']
        self.bid_button_selector.setText(selectors['bid_button'])
        self.timer_selector.setText(selectors['timer'])
        self.status_selector.setText(selectors['status'])
        self.sign_data_selector.setText(selectors['sign_data'])
        self.signature_input_selector.setText(selectors['signature_input'])
        
        # NCALayer
        self.ncalayer_port.setValue(config['ncalayer']['port'])
        self.storage_type.setCurrentText(config['ncalayer']['storage'])
        self.storage_password.setText(config['ncalayer']['password'])
        
        # Telegram
        self.telegram_enabled.setChecked(config['telegram']['enabled'])
        self.telegram_token.setText(config['telegram']['bot_token'])
        self.chat_id.setText(config['telegram']['chat_id'])
        
        # Логирование
        self.screenshots_enabled.setChecked(config['logging']['screenshots'])
    
    def save_config(self):
        """Сохранение конфигурации в файл"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить конфигурацию", "", "YAML files (*.yaml)"
        )
        if filename:
            if self.apply_config(silent=True):
                if self.config_manager.save_config(filename):
                    self.log_callback(f"💾 Конфигурация сохранена в {filename}")
                    QMessageBox.information(self, "Успех", f"Конфигурация сохранена в {filename}")
    
    def load_config(self):
        """Загрузка конфигурации из файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Загрузить конфигурацию", "", "YAML files (*.yaml)"
        )
        if filename:
            self.config_manager = ConfigManager(filename)
            self.load_current_config()
            self.log_callback(f"📂 Конфигурация загружена из {filename}")
            QMessageBox.information(self, "Успех", f"Конфигурация загружена из {filename}")
    
    def reset_config(self):
        """Сброс к настройкам по умолчанию"""
        reply = QMessageBox.question(
            self, "Подтверждение", 
            "Вы уверены, что хотите сбросить настройки к значениям по умолчанию?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager = ConfigManager()
            self.load_current_config()
            self.log_callback("🔄 Конфигурация сброшена к значениям по умолчанию")
    
    def apply_config(self, silent=False):
        """Применение изменений из формы"""
        try:
            config = self.config_manager.config
            
            # Аукцион
            config['auction']['url'] = self.auction_url.text()
            config['auction']['price_limit'] = self.price_limit.value()
            config['auction']['bid_delay'] = self.bid_delay.value()
            config['auction']['refresh_interval'] = self.refresh_interval.value()
            
            # Селекторы
            config['auction']['selectors']['bid_button'] = self.bid_button_selector.text()
            config['auction']['selectors']['timer'] = self.timer_selector.text()
            config['auction']['selectors']['status'] = self.status_selector.text()
            config['auction']['selectors']['sign_data'] = self.sign_data_selector.text()
            config['auction']['selectors']['signature_input'] = self.signature_input_selector.text()
            
            # NCALayer
            config['ncalayer']['port'] = self.ncalayer_port.value()
            config['ncalayer']['storage'] = self.storage_type.currentText()
            config['ncalayer']['password'] = self.storage_password.text()
            
            # Telegram
            config['telegram']['enabled'] = self.telegram_enabled.isChecked()
            config['telegram']['bot_token'] = self.telegram_token.text()
            config['telegram']['chat_id'] = self.chat_id.text()
            
            # Логирование
            config['logging']['screenshots'] = self.screenshots_enabled.isChecked()
            
            if not silent:
                self.log_callback("✅ Настройки применены")
                QMessageBox.information(self, "Успех", "Настройки применены!")
            return True
            
        except Exception as e:
            self.log_callback(f"❌ Ошибка применения настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить настройки: {e}")
            return False


class PyQtBotGUI(QMainWindow):
    def __init__(self, args=None):
        super().__init__()
        self.args = args
        self.config_manager = ConfigManager()
        self.bot_thread = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Auction Bot - Управление (PyQt6)")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Вкладки
        tabs = QTabWidget()
        
        # Вкладка мониторинга
        monitor_tab = self.create_monitor_tab()
        tabs.addTab(monitor_tab, "Мониторинг")
        
        # Вкладка настроек
        config_tab = ConfigTab(self.config_manager, self.add_log)
        tabs.addTab(config_tab, "Настройки")
        
        layout.addWidget(tabs)
        
        central_widget.setLayout(layout)
    
    def create_monitor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Статус
        self.status_label = QLabel("Статус: Остановлен")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.status_label)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Запуск мониторинга")
        self.stop_btn = QPushButton("⏹ Остановить")
        self.test_btn = QPushButton("⚡ Тест скорости")
        
        self.stop_btn.setEnabled(False)
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.test_btn)
        
        layout.addLayout(buttons_layout)
        
        # Лог
        log_label = QLabel("Лог выполнения:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        tab.setLayout(layout)
        
        # Подключаем кнопки
        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.test_btn.clicked.connect(self.test_speed)
        
        return tab
    
    def add_log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.append(f"{message}")
        # Автопрокрутка к последнему сообщению
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def start_bot(self):
        """Запуск бота"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Статус: Мониторинг запущен")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Индикатор прогресса
        
        # Запуск бота в отдельном потоке
        self.bot_thread = BotThread(self.config_manager)
        self.bot_thread.log_signal.connect(self.add_log)
        self.bot_thread.status_signal.connect(self.status_label.setText)
        self.bot_thread.finished_signal.connect(self.bot_finished)
        self.bot_thread.start()
        
        self.add_log("🚀 Запуск мониторинга аукциона...")
    
    def stop_bot(self):
        """Остановка бота"""
        if self.bot_thread:
            self.bot_thread.stop()
            self.add_log("⏹ Остановка мониторинга...")
    
    def bot_finished(self):
        """Завершение работы бота"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Статус: Остановлен")
        self.progress_bar.setVisible(False)
        self.add_log("🏁 Мониторинг завершен")
    
    def test_speed(self):
        """Тест скорости"""
        self.add_log("⚡ Запуск теста скорости...")
        # Здесь будет запуск теста скорости


def run_pyqt6_gui(args=None):
    """Запуск PyQt6 графического интерфейса"""
    app = QApplication(sys.argv)
    
    # Настройка asyncio для Qt
    try:
        import qasync
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
    except ImportError:
        print("qasync не установлен, используем стандартный event loop")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    window = PyQtBotGUI(args)
    window.show()
    
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    run_pyqt6_gui()
