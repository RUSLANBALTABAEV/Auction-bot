"""
Модуль для отправки уведомлений в Telegram
"""
import logging
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """Класс для отправки уведомлений в Telegram"""
    
    def __init__(self, config):
        self.config = config
        self.bot = Bot(token=config['bot_token'])
        self.chat_id = config['chat_id']
        self.logger = logging.getLogger(__name__)
    
    async def send_message(self, message):
        """Отправка сообщения в Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            self.logger.debug("Сообщение отправлено в Telegram")
        except TelegramError as e:
            self.logger.error(f"Ошибка отправки в Telegram: {e}")
            raise
