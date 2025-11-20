"""
Графический интерфейс для Auction Bot
"""
import sys
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                           QWidget, QPushButton, QTextEdit, QLabel, QLineEdit,
                           QGroupBox, QFormLayout, QCheckBox, QSpinBox)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QFont
import logging
from datetime import datetime

from bot.auction_bot import AuctionBot


class BotThread(QThread):
    """Поток для запуска бота"""
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    bid_result_signal = pyqtSignal(dict)
    
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.bot = None
        self.is_running = False
    
    def run(self):
        """Запуск бота в отдельном потоке"""
        async def run_bot():
            self.bot = AuctionBot(self.config_path)
            # Перенаправляем логи в GUI
            self.setup_bot_logging()
            await self.bot.start_monitoring()
        
        self.is_running = True
        asyncio.run(run_bot())
    
    def setup_bot_logging(self):
        """Настройка перенаправления логов бота в GUI"""
        if self.bot:
            # Добавляем обработчик, который отправляет логи в GUI
            handler = LogHandler(self.log_signal)
            self.bot.logger.addHandler(handler)
    
    def stop(self):
        """Остановка бота"""
        if self.bot:
            self.bot.is_monitoring = False
        self.is_running = False


class LogHandler(logging.Handler):
    """Обработчик логов для перенаправления в GUI"""
    def __init__(self, log_signal):
        super().__init__()
        self.log_signal = log_signal
    
    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализация UI"""
        self.setWindowTitle("Auction Bot")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Группа настроек
        settings_group = QGroupBox("Настройки")
        settings_layout = QFormLayout()
        
        self.url_input = QLineEdit("https://auction-site.com/lot/123")
        self.price_limit_input = QLineEdit("1000000")
        self.refresh_interval_input = QSpinBox()
        self.refresh_interval_input.setRange(100, 5000)
        self.refresh_interval_input.setValue(200)
        self.refresh_interval_input.setSuffix(" мс")
        
        settings_layout.addRow("URL лота:", self.url_input)
        settings_layout.addRow("Лимит цены:", self.price_limit_input)
        settings_layout.addRow("Интервал проверки:", self.refresh_interval_input)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Группа управления
        control_group = QGroupBox("Управление")
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Запуск мониторинга")
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Группа статуса
        status_group = QGroupBox("Статус")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Статус: Остановлен")
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Группа логов
        log_group = QGroupBox("Логи")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        central_widget.setLayout(layout)
        
        # Подключение сигналов
        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)
    
    def start_bot(self):
        """Запуск бота"""
        # Сохранение настроек в config.yaml (реализуйте самостоятельно)
        # ...
        
        self.bot_thread = BotThread("config.yaml")
        self.bot_thread.log_signal.connect(self.add_log)
        self.bot_thread.status_signal.connect(self.update_status)
        self.bot_thread.bid_result_signal.connect(self.handle_bid_result)
        self.bot_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.update_status("Мониторинг запущен")
        self.add_log("Бот запущен")
    
    def stop_bot(self):
        """Остановка бота"""
        if self.bot_thread:
            self.bot_thread.stop()
            self.bot_thread.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.update_status("Остановлен")
        self.add_log("Бот остановлен")
    
    def add_log(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Автопрокрутка к последнему сообщению
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def update_status(self, status):
        """Обновление статуса"""
        self.status_label.setText(f"Статус: {status}")
    
    def handle_bid_result(self, result):
        """Обработка результата подачи ставки"""
        if result['success']:
            self.add_log(f"✅ Ставка подана! Время: {result['reaction_time']} мс")
        else:
            self.add_log(f"❌ Ошибка: {result['error']}")


def run_gui():
    """Запуск графического интерфейса"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
