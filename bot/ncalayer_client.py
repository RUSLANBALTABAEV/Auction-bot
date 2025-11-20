"""
Клиент для работы с NCALayer с поддержкой callback
"""
import aiohttp
import asyncio
import logging
import urllib.parse
import os
import subprocess
from aiohttp import web
import json


class NCALayerClient:
    """Клиент для взаимодействия с NCALayer с поддержкой callback сервера"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.callback_server = None
        self.callback_port = 13580  # Порт для callback сервера
        self.signature_received = asyncio.Event()
        self.received_signature = None
    
    async def sign_data(self, data_to_sign):
        """Подписание данных через NCALayer с использованием callback"""
        try:
            # Запускаем callback сервер, если еще не запущен
            if not self.callback_server:
                await self.start_callback_server()
            
            # Формируем URL для callback
            callback_url = f"http://localhost:{self.callback_port}/ncalayer_callback"
            
            # Формируем URL для вызова NCALayer
            ncalayer_url = (
                f"ncalayer://sign?data={urllib.parse.quote(data_to_sign)}"
                f"&callback={urllib.parse.quote(callback_url)}"
            )
            
            # Вызываем NCALayer
            if os.name == 'nt':  # Windows
                subprocess.Popen(['start', ncalayer_url], shell=True)
            else:  # Linux/Mac
                import webbrowser
                webbrowser.open(ncalayer_url)
            
            self.logger.info("Запрос на подпись отправлен в NCALayer")
            
            # Ждем, пока callback сервер получит подпись (таймаут 30 секунд)
            try:
                await asyncio.wait_for(self.signature_received.wait(), timeout=30.0)
                return self.received_signature
            except asyncio.TimeoutError:
                raise Exception("Таймаут ожидания подписи от NCALayer")
            
        except Exception as e:
            self.logger.error(f"Ошибка подписи через NCALayer: {e}")
            raise
    
    async def start_callback_server(self):
        """Запуск встроенного HTTP сервера для обработки callback от NCALayer"""
        app = web.Application()
        app.router.add_post('/ncalayer_callback', self.handle_callback)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.callback_port)
        await site.start()
        
        self.callback_server = runner
        self.logger.info(f"Callback сервер запущен на порту {self.callback_port}")
    
    async def handle_callback(self, request):
        """Обработка callback от NCALayer"""
        try:
            data = await request.json()
            self.logger.info("Получен callback от NCALayer")
            
            # Предполагаем, что подпись находится в поле 'signature'
            signature = data.get('signature')
            if signature:
                self.received_signature = signature
                self.signature_received.set()
                return web.Response(text=json.dumps({'status': 'success'}), status=200)
            else:
                self.logger.error("В callback от NCALayer отсутствует подпись")
                return web.Response(text=json.dumps({'status': 'error'}), status=400)
                
        except Exception as e:
            self.logger.error(f"Ошибка обработки callback: {e}")
            return web.Response(text=json.dumps({'status': 'error'}), status=500)
    
    async def close(self):
        """Закрытие callback сервера"""
        if self.callback_server:
            await self.callback_server.cleanup()
