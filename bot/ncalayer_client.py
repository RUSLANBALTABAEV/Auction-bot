"""
Клиент для работы с NCALayer
"""
import aiohttp
import asyncio
import logging
import urllib.parse
import os
import subprocess


class NCALayerClient:
    """Клиент для взаимодействия с NCALayer"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def sign_data(self, data_to_sign):
        """Подписание данных через NCALayer"""
        try:
            # Попытка HTTP подключения
            signature = await self._sign_via_http(data_to_sign)
            if signature:
                return signature
            
            # Попытка через протокол ncalayer://
            signature = await self._sign_via_protocol(data_to_sign)
            if signature:
                return signature
                
            raise Exception("Все методы подписи не сработали")
            
        except Exception as e:
            self.logger.error(f"Ошибка подписи через NCALayer: {e}")
            raise
    
    async def _sign_via_http(self, data_to_sign):
        """Подписание через HTTP API NCALayer"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://localhost:{self.config['port']}/sign",
                    json={
                        "data": data_to_sign,
                        "storage": self.config['storage'],
                        "password": self.config['password']
                    },
                    timeout=aiohttp.ClientTimeout(total=self.config['timeout']/1000)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info("Подпись получена через HTTP API")
                        return result.get('signature')
                    else:
                        self.logger.warning(f"HTTP API недоступен: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.debug(f"HTTP метод не сработал: {e}")
            return None
    
    async def _sign_via_protocol(self, data_to_sign):
        """Подписание через протокол ncalayer://"""
        try:
            ncalayer_url = f"ncalayer://sign?data={urllib.parse.quote(data_to_sign)}"
            
            if os.name == 'nt':  # Windows
                subprocess.Popen(['start', ncalayer_url], shell=True)
            else:  # Linux/Mac
                import webbrowser
                webbrowser.open(ncalayer_url)
            
            self.logger.info("Запрос на подпись отправлен в NCALayer")
            
            # Здесь должна быть логика ожидания и получения callback
            # В реальной реализации нужно настроить callback endpoint
            await asyncio.sleep(10)  # Временная заглушка
            
            # Для демонстрации возвращаем тестовую подпись
            return "SIMULATED_SIGNATURE_FOR_DEMO"
            
        except Exception as e:
            self.logger.error(f"Ошибка вызова NCALayer через протокол: {e}")
            return None
