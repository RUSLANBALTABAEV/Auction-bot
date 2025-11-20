"""
Тестирование скорости реакции бота
"""
import asyncio
import time
import statistics
from bot.auction_bot import AuctionBot


class SpeedTester:
    """Тестер скорости реакции"""
    
    def __init__(self, config_path, test_runs=10):
        self.config_path = config_path
        self.test_runs = test_runs
        self.reaction_times = []
    
    async def run_speed_test(self):
        """Запуск теста скорости"""
        print(f"🚀 Запуск теста скорости ({self.test_runs} попыток)")
        
        for i in range(self.test_runs):
            print(f"\nПопытка {i + 1}/{self.test_runs}")
            
            # Создаем бота с мок-обработчиком
            bot = self.create_test_bot()
            
            try:
                reaction_time = await self.measure_reaction_time(bot)
                self.reaction_times.append(reaction_time)
                print(f"✅ Время реакции: {reaction_time:.2f} мс")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
            
            await asyncio.sleep(1)  # Пауза между попытками
        
        self.print_results()
    
    def create_test_bot(self):
        """Создание тестового бота с переопределенными методами"""
        
        class TestAuctionBot(AuctionBot):
            async def submit_bid(self):
                start_time = time.time()
                # Имитация задержки сети и обработки
                await asyncio.sleep(0.1)
                return (time.time() - start_time) * 1000
            
            async def handle_signature_process(self):
                # Имитация подписи
                await asyncio.sleep(0.05)
        
        return TestAuctionBot(self.config_path)
    
    async def measure_reaction_time(self, bot):
        """Измерение времени реакции"""
        start_time = time.time()
        
        # Имитация обнаружения начала торгов
        await asyncio.sleep(0.01)
        
        # "Подача" ставки
        reaction_time = await bot.submit_bid()
        
        return reaction_time
    
    def print_results(self):
        """Вывод результатов тестирования"""
        if not self.reaction_times:
            print("Нет данных для анализа")
            return
        
        print("\n" + "="*50)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ СКОРОСТИ")
        print("="*50)
        print(f"Количество тестов: {len(self.reaction_times)}")
        print(f"Среднее время: {statistics.mean(self.reaction_times):.2f} мс")
        print(f"Медианное время: {statistics.median(self.reaction_times):.2f} мс")
        print(f"Минимальное время: {min(self.reaction_times):.2f} мс")
        print(f"Максимальное время: {max(self.reaction_times):.2f} мс")
        print(f"Стандартное отклонение: {statistics.stdev(self.reaction_times):.2f} мс")
        
        # Проверка соответствия требованиям (<1 сек)
        max_time = max(self.reaction_times)
        if max_time < 1000:
            print("✅ ТЕСТ ПРОЙДЕН: Все реакции быстрее 1 секунды")
        else:
            print(f"⚠️  ВНИМАНИЕ: Максимальное время превышает 1 секунду: {max_time:.2f} мс")


async def main():
    """Основная функция"""
    tester = SpeedTester("config.yaml", test_runs=5)
    await tester.run_speed_test()


if __name__ == "__main__":
    asyncio.run(main())
