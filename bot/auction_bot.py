"""
Основной класс бота для аукциона
"""
import asyncio
import time
import logging
from playwright.async_api import async_playwright
import os
from datetime import datetime

from utils.telegram_notifier import TelegramNotifier
from bot.ncalayer_client import NCALayerClient


class AuctionBot:
    """Класс бота для автоматической подачи ставок на аукционе"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.config = config_manager.config
        self.setup_directories()
        self.setup_logging()
        self.setup_notifiers()
        self.ncalayer_client = NCALayerClient(self.config['ncalayer'])
        
        self.browser = None
        self.page = None
        self.is_monitoring = False
        self.bid_submitted = False
        self.start_time = None
        
    def setup_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.config['logging']['screenshots_path'], exist_ok=True)
    
    def setup_logging(self):
        """Настройка системы логирования"""
        log_level = getattr(logging, self.config['logging']['level'])
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['logging']['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Логируем информацию о конфигурации
        self.logger.info("Бот инициализирован с конфигурацией:")
        self.logger.info(f"URL: {self.config['auction']['url']}")
        self.logger.info(f"Лимит цены: {self.config['auction']['price_limit']:,}")
        self.logger.info(f"Telegram: {'Включен' if self.config['telegram']['enabled'] else 'Выключен'}")
    
    def setup_notifiers(self):
        """Настройка системы уведомлений"""
        self.telegram_notifier = TelegramNotifier(self.config['telegram']) if self.config['telegram']['enabled'] else None
    
    async def send_notification(self, message):
        """Отправка уведомлений"""
        self.logger.info(message)
        
        if self.telegram_notifier:
            try:
                await self.telegram_notifier.send_message(message)
            except Exception as e:
                self.logger.error(f"Ошибка отправки Telegram: {e}")
    
    async def start_monitoring(self):
        """Запуск мониторинга аукциона"""
        self.start_time = datetime.now()
        await self.send_notification(f"🚀 Мониторинг аукциона запущен\nВремя: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        async with async_playwright() as p:
            # Запуск браузера
            self.browser = await p.chromium.launch(
                headless=self.config['browser']['headless'],
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Создание страницы
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            await self.page.set_extra_http_headers({
                'User-Agent': self.config['browser']['user_agent']
            })
            
            # Переход на страницу аукциона
            self.logger.info(f"Переход на страницу: {self.config['auction']['url']}")
            await self.page.goto(
                self.config['auction']['url'],
                wait_until='networkidle',
                timeout=self.config['browser']['timeout']
            )
            
            # Основной цикл мониторинга
            self.is_monitoring = True
            await self.monitoring_loop()
    
    async def monitoring_loop(self):
        """Основной цикл мониторинга"""
        monitoring_start = time.time()
        
        while self.is_monitoring and not self.bid_submitted:
            try:
                # Проверка статуса аукциона
                auction_started = await self.check_auction_status()
                
                if auction_started and not self.bid_submitted:
                    await self.submit_bid()
                
                # Проверка таймаута мониторинга (например, 1 час)
                if time.time() - monitoring_start > 3600:
                    await self.send_notification("⏰ Мониторинг остановлен по таймауту (1 час)")
                    break
                    
                # Задержка между проверками
                await asyncio.sleep(self.config['auction']['refresh_interval'] / 1000)
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(1)  # Пауза при ошибке
    
    async def check_auction_status(self):
        """Проверка статуса аукциона"""
        try:
            # Метод 1: Проверка активной кнопки ставки
            bid_button = await self.page.query_selector(
                self.config['auction']['selectors']['bid_button']
            )
            
            if bid_button and await bid_button.is_enabled():
                self.logger.info("🎯 Обнаружена активная кнопка ставки!")
                return True
            
            # Метод 2: Проверка таймера
            timer_element = await self.page.query_selector(
                self.config['auction']['selectors']['timer']
            )
            if timer_element:
                timer_text = await timer_element.text_content()
                if self.is_timer_expired(timer_text):
                    self.logger.info("⏰ Таймер истек - начало торгов!")
                    return True
            
            # Метод 3: Проверка статуса
            status_element = await self.page.query_selector(
                self.config['auction']['selectors']['status']
            )
            if status_element:
                status_text = await status_element.text_content()
                if "начался" in status_text.lower() or "старт" in status_text.lower():
                    self.logger.info("📢 Объявлено начало торгов!")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки статуса аукциона: {e}")
            return False
    
    def is_timer_expired(self, timer_text):
        """Проверка истечения таймера"""
        if not timer_text:
            return False
            
        timer_text = timer_text.strip().lower()
        
        # Проверка различных форматов таймера
        expired_indicators = [
            "00:00:00", "00:00", "0:00", 
            "время вышло", "таймер истек", "завершено",
            "start", "начало"
        ]
        
        return any(indicator in timer_text for indicator in expired_indicators)
    
    async def submit_bid(self):
        """Подача ставки +1 шаг"""
        bid_start_time = time.time()
        
        try:
            await self.send_notification("⚡ Начало торгов! Подача ставки...")
            
            # Скриншот перед подачей
            await self.take_screenshot("before_bid")
            
            # Нажатие кнопки подачи ставки
            await self.page.click(
                self.config['auction']['selectors']['bid_button'],
                timeout=5000
            )
            self.logger.info("✅ Кнопка ставки нажата")
            
            # Обработка подписи
            await self.handle_signature_process()
            
            # Подтверждение ставки
            confirmation_success = await self.confirm_bid()
            
            if confirmation_success:
                self.bid_submitted = True
                bid_time = (time.time() - bid_start_time) * 1000
                
                success_message = (
                    f"✅ Ставка успешно подана!\n"
                    f"⏱ Время реакции: {bid_time:.2f} мс\n"
                    f"🏁 Общее время мониторинга: {(datetime.now() - self.start_time).total_seconds():.1f} сек"
                )
                
                await self.send_notification(success_message)
                await self.take_screenshot("bid_success")
                
                # Запись в лог
                self.log_bid_result(success=True, reaction_time=bid_time)
            else:
                raise Exception("Не удалось подтвердить ставку")
                
        except Exception as e:
            error_message = f"❌ Ошибка подачи ставки: {e}"
            self.logger.error(error_message)
            await self.send_notification(error_message)
            await self.take_screenshot("bid_error")
            self.log_bid_result(success=False, error=str(e))
    
    async def handle_signature_process(self):
        """Обработка процесса подписи через NCALayer"""
        try:
            # Ожидание появления формы подписи
            await self.page.wait_for_selector(
                self.config['auction']['selectors']['sign_data'],
                timeout=10000
            )
            
            # Получение данных для подписи
            sign_data_element = await self.page.query_selector(
                self.config['auction']['selectors']['sign_data']
            )
            sign_data = await sign_data_element.get_attribute('value')
            
            if not sign_data:
                raise Exception("Данные для подписи не найдены")
            
            self.logger.info(f"Получены данные для подписи ({len(sign_data)} символов)")
            
            # Вызов NCALayer для подписи
            signature = await self.ncalayer_client.sign_data(sign_data)
            
            if not signature:
                raise Exception("Не удалось получить подпись от NCALayer")
            
            # Ввод подписи в форму
            await self.page.fill(
                self.config['auction']['selectors']['signature_input'],
                signature
            )
            
            self.logger.info("✅ Подпись успешно применена")
            
        except Exception as e:
            self.logger.error(f"Ошибка процесса подписи: {e}")
            raise
    
    async def confirm_bid(self):
        """Подтверждение ставки после подписи"""
        try:
            # Здесь должна быть логика подтверждения ставки
            # Зависит от конкретной площадки
            
            # Пример: нажатие кнопки подтверждения
            confirm_button = await self.page.query_selector('button[type="submit"]')
            if confirm_button:
                await confirm_button.click()
                await self.page.wait_for_timeout(3000)  # Ожидание обработки
                
            # Проверка успешности
            success_indicator = await self.page.query_selector('.success-message, .bid-confirmed')
            return success_indicator is not None
            
        except Exception as e:
            self.logger.error(f"Ошибка подтверждения ставки: {e}")
            return False
    
    async def take_screenshot(self, name):
        """Создание скриншота"""
        if self.config['logging']['screenshots']:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{name}_{timestamp}.png"
                path = os.path.join(self.config['logging']['screenshots_path'], filename)
                await self.page.screenshot(path=path)
                self.logger.debug(f"Скриншот сохранен: {path}")
            except Exception as e:
                self.logger.error(f"Ошибка создания скриншота: {e}")
    
    def log_bid_result(self, success=True, reaction_time=None, error=None):
        """Логирование результата подачи ставки"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'reaction_time_ms': reaction_time,
            'error': error,
            'url': self.config['auction']['url'],
            'price_limit': self.config['auction']['price_limit']
        }
        
        # Запись в отдельный лог-файл результатов
        results_log = "bid_results.log"
        with open(results_log, 'a', encoding='utf-8') as f:
            f.write(f"{log_entry}\n")
    
    async def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_monitoring = False
        if self.browser:
            await self.browser.close()
        
        await self.send_notification("🛑 Мониторинг остановлен")
