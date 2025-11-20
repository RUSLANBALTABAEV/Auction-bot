"""
Мониторинг производительности и скорости реакции
"""
import time
import asyncio
import statistics
from datetime import datetime
import logging


class PerformanceMonitor:
    """Монитор производительности бота"""
    
    def __init__(self):
        self.reaction_times = []
        self.detection_times = []
        self.bid_success_rate = 0
        self.total_bids = 0
        self.successful_bids = 0
        self.start_time = None
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self):
        """Начало мониторинга"""
        self.start_time = datetime.now()
        self.logger.info("🚀 Мониторинг производительности запущен")
    
    def record_reaction_time(self, reaction_time_ms):
        """Запись времени реакции"""
        self.reaction_times.append(reaction_time_ms)
        self.logger.info(f"⏱ Время реакции: {reaction_time_ms:.2f} мс")
    
    def record_detection_time(self, detection_time_ms):
        """Запись времени обнаружения"""
        self.detection_times.append(detection_time_ms)
    
    def record_bid_result(self, success):
        """Запись результата ставки"""
        self.total_bids += 1
        if success:
            self.successful_bids += 1
        self.bid_success_rate = (self.successful_bids / self.total_bids) * 100
    
    def get_performance_report(self):
        """Получение отчета о производительности"""
        if not self.reaction_times:
            return "Нет данных о производительности"
        
        report = [
            "📊 ОТЧЕТ ПРОИЗВОДИТЕЛЬНОСТИ",
            f"Общее время работы: {(datetime.now() - self.start_time).total_seconds():.1f} сек",
            f"Всего ставок: {self.total_bids}",
            f"Успешных ставок: {self.successful_bids}",
            f"Процент успеха: {self.bid_success_rate:.1f}%",
            f"Среднее время реакции: {statistics.mean(self.reaction_times):.2f} мс",
            f"Медианное время реакции: {statistics.median(self.reaction_times):.2f} мс",
            f"Минимальное время: {min(self.reaction_times):.2f} мс",
            f"Максимальное время: {max(self.reaction_times):.2f} мс",
            f"Стандартное отклонение: {statistics.stdev(self.reaction_times) if len(self.reaction_times) > 1 else 0:.2f} мс"
        ]
        
        return "\n".join(report)
    
    def save_performance_log(self, filename="performance.log"):
        """Сохранение лога производительности"""
        report = self.get_performance_report()
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"\n{datetime.now().isoformat()}\n")
            f.write(report)
            f.write("\n" + "="*50 + "\n")
        
        self.logger.info("Отчет производительности сохранен")


# Интеграция с основным ботом
def add_performance_monitoring(bot_class):
    """Декоратор для добавления мониторинга производительности"""
    class MonitoringAuctionBot(bot_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.performance_monitor = PerformanceMonitor()
        
        async def start_monitoring(self):
            self.performance_monitor.start_monitoring()
            await super().start_monitoring()
            # После завершения - сохраняем отчет
            self.performance_monitor.save_performance_log()
        
        async def submit_bid(self):
            start_time = time.time()
            try:
                await super().submit_bid()
                reaction_time = (time.time() - start_time) * 1000
                self.performance_monitor.record_reaction_time(reaction_time)
                self.performance_monitor.record_bid_result(True)
            except Exception as e:
                reaction_time = (time.time() - start_time) * 1000
                self.performance_monitor.record_reaction_time(reaction_time)
                self.performance_monitor.record_bid_result(False)
                raise
    
    return MonitoringAuctionBot
