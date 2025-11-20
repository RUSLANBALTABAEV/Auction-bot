"""
Графический интерфейс на Tkinter для Auction Bot
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import ConfigManager


class TkinterBotGUI:
    def __init__(self, root, args=None):
        self.root = root
        self.args = args
        self.config_manager = ConfigManager()
        self.bot_thread = None
        self.is_running = False
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.root.title("Auction Bot - Управление (Tkinter)")
        self.root.geometry("900x700")
        
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка мониторинга
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text='Мониторинг')
        self.setup_monitor_tab()
        
        # Вкладка настроек
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text='Настройки')
        self.setup_config_tab()
    
    def setup_monitor_tab(self):
        """Настройка вкладки мониторинга"""
        frame = self.monitor_frame
        
        # Статус
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(status_frame, text="Статус:", font=('Arial', 12, 'bold')).pack(side='left')
        self.status_label = ttk.Label(status_frame, text="Остановлен", font=('Arial', 12, 'bold'), foreground='red')
        self.status_label.pack(side='left', padx=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="🚀 Запуск мониторинга", command=self.start_bot)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Остановить", command=self.stop_bot, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        self.test_btn = ttk.Button(button_frame, text="⚡ Тест скорости", command=self.test_speed)
        self.test_btn.pack(side='left', padx=5)
        
        # Лог выполнения
        log_frame = ttk.LabelFrame(frame, text="Лог выполнения", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80, font=('Consolas', 10))
        self.log_text.pack(fill='both', expand=True)
    
    def setup_config_tab(self):
        """Настройка вкладки конфигурации"""
        frame = self.config_frame
        
        # Создаем фрейм с прокруткой
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Настройки аукциона
        auction_frame = ttk.LabelFrame(scrollable_frame, text="Настройки аукциона", padding=10)
        auction_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(auction_frame, text="URL аукциона:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.url_entry = ttk.Entry(auction_frame, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(auction_frame, text="Лимит цены:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.price_limit_var = tk.StringVar()
        self.price_limit_spin = ttk.Spinbox(auction_frame, from_=0, to=1000000000, increment=1000, 
                                           textvariable=self.price_limit_var, width=20)
        self.price_limit_spin.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(auction_frame, text="Задержка подачи (мс):").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.bid_delay_var = tk.StringVar()
        self.bid_delay_spin = ttk.Spinbox(auction_frame, from_=0, to=5000, increment=50, 
                                         textvariable=self.bid_delay_var, width=20)
        self.bid_delay_spin.grid(row=2, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(auction_frame, text="Интервал проверки (мс):").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.refresh_interval_var = tk.StringVar()
        self.refresh_interval_spin = ttk.Spinbox(auction_frame, from_=50, to=5000, increment=50, 
                                                textvariable=self.refresh_interval_var, width=20)
        self.refresh_interval_spin.grid(row=3, column=1, padx=5, pady=2, sticky='w')
        
        # Селекторы
        selectors_frame = ttk.LabelFrame(scrollable_frame, text="Селекторы", padding=10)
        selectors_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(selectors_frame, text="Кнопка ставки:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.bid_button_entry = ttk.Entry(selectors_frame, width=60)
        self.bid_button_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(selectors_frame, text="Таймер:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.timer_entry = ttk.Entry(selectors_frame, width=60)
        self.timer_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(selectors_frame, text="Статус:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.status_entry = ttk.Entry(selectors_frame, width=60)
        self.status_entry.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(selectors_frame, text="Данные для подписи:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.sign_data_entry = ttk.Entry(selectors_frame, width=60)
        self.sign_data_entry.grid(row=3, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(selectors_frame, text="Поле подписи:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.signature_input_entry = ttk.Entry(selectors_frame, width=60)
        self.signature_input_entry.grid(row=4, column=1, padx=5, pady=2, sticky='ew')
        
        # Настройки NCALayer
        ncalayer_frame = ttk.LabelFrame(scrollable_frame, text="Настройки NCALayer", padding=10)
        ncalayer_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(ncalayer_frame, text="Порт NCALayer:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.ncalayer_port_var = tk.StringVar()
        self.ncalayer_port_spin = ttk.Spinbox(ncalayer_frame, from_=1, to=65535, 
                                             textvariable=self.ncalayer_port_var, width=20)
        self.ncalayer_port_spin.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(ncalayer_frame, text="Тип хранилища:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.storage_type_combo = ttk.Combobox(ncalayer_frame, values=["PKCS12", "PKCS8"], width=18)
        self.storage_type_combo.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(ncalayer_frame, text="Пароль хранилища:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.storage_password_entry = ttk.Entry(ncalayer_frame, show="*", width=30)
        self.storage_password_entry.grid(row=2, column=1, padx=5, pady=2, sticky='w')
        
        # Настройки Telegram
        telegram_frame = ttk.LabelFrame(scrollable_frame, text="Настройки Telegram", padding=10)
        telegram_frame.pack(fill='x', padx=10, pady=5)
        
        self.telegram_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(telegram_frame, text="Включить Telegram уведомления", 
                       variable=self.telegram_enabled_var, command=self.toggle_telegram_fields).grid(row=0, column=0, sticky='w', columnspan=2)
        
        ttk.Label(telegram_frame, text="Token бота:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.telegram_token_entry = ttk.Entry(telegram_frame, width=60)
        self.telegram_token_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        
        ttk.Label(telegram_frame, text="Chat ID:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.chat_id_entry = ttk.Entry(telegram_frame, width=60)
        self.chat_id_entry.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        
        # Информация о Telegram
        telegram_info = ("Для настройки Telegram:\n"
                        "1. Создайте бота через @BotFather\n"
                        "2. Получите token\n" 
                        "3. Узнайте ваш chat ID через @userinfobot")
        telegram_info_label = ttk.Label(telegram_frame, text=telegram_info, background='#f0f0f0', padding=10)
        telegram_info_label.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        # Настройки логирования
        logging_frame = ttk.LabelFrame(scrollable_frame, text="Логирование", padding=10)
        logging_frame.pack(fill='x', padx=10, pady=5)
        
        self.screenshots_var = tk.BooleanVar()
        ttk.Checkbutton(logging_frame, text="Сохранять скриншоты", 
                       variable=self.screenshots_var).grid(row=0, column=0, sticky='w')
        
        # Кнопки управления конфигурацией
        config_buttons_frame = ttk.Frame(scrollable_frame)
        config_buttons_frame.pack(fill='x', padx=10, pady=20)
        
        ttk.Button(config_buttons_frame, text="💾 Сохранить конфигурацию", 
                  command=self.save_config_dialog).pack(side='left', padx=5)
        ttk.Button(config_buttons_frame, text="📂 Загрузить конфигурацию", 
                  command=self.load_config_dialog).pack(side='left', padx=5)
        ttk.Button(config_buttons_frame, text="🔄 Сбросить настройки", 
                  command=self.reset_config).pack(side='left', padx=5)
        ttk.Button(config_buttons_frame, text="✅ Применить настройки", 
                  command=self.apply_config).pack(side='left', padx=5)
        
        # Упаковка скролла
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Настройка веса для растягивания
        scrollable_frame.columnconfigure(1, weight=1)
        auction_frame.columnconfigure(1, weight=1)
        selectors_frame.columnconfigure(1, weight=1)
        telegram_frame.columnconfigure(1, weight=1)
    
    def toggle_telegram_fields(self):
        """Включение/выключение полей Telegram"""
        state = 'normal' if self.telegram_enabled_var.get() else 'disabled'
        self.telegram_token_entry.config(state=state)
        self.chat_id_entry.config(state=state)
    
    def load_config(self):
        """Загрузка конфигурации в форму"""
        config = self.config_manager.config
        
        # Аукцион
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, config['auction']['url'])
        
        self.price_limit_var.set(str(config['auction']['price_limit']))
        self.bid_delay_var.set(str(config['auction']['bid_delay']))
        self.refresh_interval_var.set(str(config['auction']['refresh_interval']))
        
        # Селекторы
        selectors = config['auction']['selectors']
        self.bid_button_entry.delete(0, tk.END)
        self.bid_button_entry.insert(0, selectors['bid_button'])
        
        self.timer_entry.delete(0, tk.END)
        self.timer_entry.insert(0, selectors['timer'])
        
        self.status_entry.delete(0, tk.END)
        self.status_entry.insert(0, selectors['status'])
        
        self.sign_data_entry.delete(0, tk.END)
        self.sign_data_entry.insert(0, selectors['sign_data'])
        
        self.signature_input_entry.delete(0, tk.END)
        self.signature_input_entry.insert(0, selectors['signature_input'])
        
        # NCALayer
        self.ncalayer_port_var.set(str(config['ncalayer']['port']))
        self.storage_type_combo.set(config['ncalayer']['storage'])
        self.storage_password_entry.delete(0, tk.END)
        self.storage_password_entry.insert(0, config['ncalayer']['password'])
        
        # Telegram
        self.telegram_enabled_var.set(config['telegram']['enabled'])
        self.telegram_token_entry.delete(0, tk.END)
        self.telegram_token_entry.insert(0, config['telegram']['bot_token'])
        self.chat_id_entry.delete(0, tk.END)
        self.chat_id_entry.insert(0, config['telegram']['chat_id'])
        self.toggle_telegram_fields()
        
        # Логирование
        self.screenshots_var.set(config['logging']['screenshots'])
    
    def apply_config(self):
        """Применение настроек из формы"""
        try:
            config = self.config_manager.config
            
            # Аукцион
            config['auction']['url'] = self.url_entry.get()
            config['auction']['price_limit'] = int(self.price_limit_var.get())
            config['auction']['bid_delay'] = int(self.bid_delay_var.get())
            config['auction']['refresh_interval'] = int(self.refresh_interval_var.get())
            
            # Селекторы
            config['auction']['selectors']['bid_button'] = self.bid_button_entry.get()
            config['auction']['selectors']['timer'] = self.timer_entry.get()
            config['auction']['selectors']['status'] = self.status_entry.get()
            config['auction']['selectors']['sign_data'] = self.sign_data_entry.get()
            config['auction']['selectors']['signature_input'] = self.signature_input_entry.get()
            
            # NCALayer
            config['ncalayer']['port'] = int(self.ncalayer_port_var.get())
            config['ncalayer']['storage'] = self.storage_type_combo.get()
            config['ncalayer']['password'] = self.storage_password_entry.get()
            
            # Telegram
            config['telegram']['enabled'] = self.telegram_enabled_var.get()
            config['telegram']['bot_token'] = self.telegram_token_entry.get()
            config['telegram']['chat_id'] = self.chat_id_entry.get()
            
            # Логирование
            config['logging']['screenshots'] = self.screenshots_var.get()
            
            # Сохраняем конфигурацию
            if self.config_manager.save_config():
                self.log("✅ Настройки применены и сохранены")
                messagebox.showinfo("Успех", "Настройки применены и сохранены!")
            else:
                raise Exception("Не удалось сохранить конфигурацию")
                
        except Exception as e:
            self.log(f"❌ Ошибка применения настроек: {e}")
            messagebox.showerror("Ошибка", f"Не удалось применить настройки: {e}")
    
    def save_config_dialog(self):
        """Сохранение конфигурации в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            title="Сохранить конфигурацию"
        )
        if filename:
            self.apply_config()
            if self.config_manager.save_config(filename):
                self.log(f"💾 Конфигурация сохранена в {filename}")
                messagebox.showinfo("Успех", f"Конфигурация сохранена в {filename}")
    
    def load_config_dialog(self):
        """Загрузка конфигурации из файла"""
        filename = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")],
            title="Загрузить конфигурацию"
        )
        if filename:
            self.config_manager = ConfigManager(filename)
            self.load_config()
            self.log(f"📂 Конфигурация загружена из {filename}")
            messagebox.showinfo("Успех", f"Конфигурация загружена из {filename}")
    
    def reset_config(self):
        """Сброс настроек к значениям по умолчанию"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить настройки к значениям по умолчанию?"):
            self.config_manager = ConfigManager()
            self.load_config()
            self.log("🔄 Настройки сброшены к значениям по умолчанию")
    
    def log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_bot(self):
        """Запуск бота"""
        if self.is_running:
            messagebox.showwarning("Внимание", "Бот уже запущен!")
            return
        
        # Применяем настройки перед запуском
        self.apply_config()
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Запущен", foreground='green')
        
        # Запускаем бота в отдельном потоке
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()
        
        self.log("🚀 Запуск мониторинга аукциона...")
    
    def run_bot(self):
        """Запуск бота в отдельном потоке"""
        async def async_run():
            try:
                from bot.auction_bot import AuctionBot
                bot = AuctionBot(self.config_manager)
                await bot.start_monitoring()
            except Exception as e:
                self.log(f"❌ Ошибка при работе бота: {e}")
            finally:
                self.bot_finished()
        
        # Создаем новый event loop для потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_run())
        finally:
            loop.close()
    
    def stop_bot(self):
        """Остановка бота"""
        self.log("⏹ Остановка мониторинга...")
        self.is_running = False
        # Здесь должна быть логика остановки бота
    
    def bot_finished(self):
        """Завершение работы бота"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Остановлен", foreground='red')
        self.log("🏁 Мониторинг завершен")
    
    def test_speed(self):
        """Тест скорости"""
        self.log("⚡ Запуск теста скорости...")
        # Здесь будет запуск теста скорости


def run_tkinter_gui(args=None):
    """Запуск Tkinter графического интерфейса"""
    root = tk.Tk()
    app = TkinterBotGUI(root, args)
    root.mainloop()


if __name__ == "__main__":
    run_tkinter_gui()
