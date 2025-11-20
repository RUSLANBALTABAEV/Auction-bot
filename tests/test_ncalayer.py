"""
Тесты для NCALayerClient
"""
import pytest
import asyncio
from bot.ncalayer_client import NCALayerClient


class TestNCALayerClient:
    """Тесты для NCALayerClient"""
    
    @pytest.fixture
    async def ncalayer_client(self):
        """Создание клиента для тестов"""
        config = {
            'port': 13579,
            'storage': 'PKCS12',
            'password': '',
            'timeout': 30000
        }
        client = NCALayerClient(config)
        yield client
        await client.close()
    
    @pytest.mark.asyncio
    async def test_callback_server(self, ncalayer_client):
        """Тест работы callback сервера"""
        # Запускаем сервер
        await ncalayer_client.start_callback_server()
        
        # Проверяем, что сервер запущен
        assert ncalayer_client.callback_server is not None
        
        # Имитируем callback запрос
        test_signature = "test_signature"
        await ncalayer_client.handle_callback({
            'signature': test_signature
        })
        
        # Проверяем, что подпись получена
        assert ncalayer_client.received_signature == test_signature
        assert ncalayer_client.signature_received.is_set()
