"""
Тесты для аукционного бота
"""
import pytest
import asyncio
from bot.auction_bot import AuctionBot
from config_manager import ConfigManager


class TestAuctionBot:
    """Тесты для AuctionBot"""
    
    @pytest.fixture
    async def bot(self):
        """Создание экземпляра бота для тестов"""
        config_manager = ConfigManager()
        bot = AuctionBot(config_manager)
        yield bot
        if bot.browser:
            await bot.browser.close()
    
    @pytest.mark.asyncio
    async def test_bot_initialization(self, bot):
        """Тест инициализации бота"""
        assert bot is not None
        assert bot.config is not None
        assert bot.is_monitoring is False
    
    @pytest.mark.asyncio 
    async def test_timer_expiration_detection(self, bot):
        """Тест определения истечения таймера"""
        assert bot.is_timer_expired("00:00:00") == True
        assert bot.is_timer_expired("00:00") == True
        assert bot.is_timer_expired("время вышло") == True
        assert bot.is_timer_expired("01:30:00") == False
        assert bot.is_timer_expired("") == False


if __name__ == "__main__":
    pytest.main([__file__])
