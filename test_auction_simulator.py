"""
Симулятор аукциона для тестирования скорости реакции
"""
from flask import Flask, render_template_string, request
import threading
import time
import webbrowser
from datetime import datetime, timedelta


class AuctionSimulator:
    """Симулятор аукционной площадки для тестирования"""
    
    def __init__(self, port=5000):
        self.port = port
        self.app = Flask(__name__)
        self.auction_start_time = None
        self.bid_received_time = None
        self.setup_routes()
    
    def setup_routes(self):
        """Настройка маршрутов симулятора"""
        
        @self.app.route('/')
        def auction_page():
            """Страница аукциона"""
            current_time = datetime.now()
            
            # Если аукцион еще не начался
            if not self.auction_start_time or current_time < self.auction_start_time:
                time_until_start = (self.auction_start_time - current_time).total_seconds() if self.auction_start_time else 0
                timer_text = f"{int(time_until_start):02d}:{int((time_until_start % 1) * 100):02d}"
                button_disabled = "disabled"
                status = "До начала:"
            else:
                timer_text = "00:00"
                button_disabled = ""
                status = "АУКЦИОН НАЧАЛСЯ!"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Тестовый аукцион</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .timer { font-size: 24px; color: #333; margin: 20px 0; }
                    .status { font-size: 18px; color: #666; }
                    .bid-button { 
                        padding: 15px 30px; 
                        font-size: 18px; 
                        background-color: #4CAF50; 
                        color: white; 
                        border: none; 
                        cursor: pointer; 
                        margin: 20px 0;
                    }
                    .bid-button:disabled { 
                        background-color: #cccccc; 
                        cursor: not-allowed; 
                    }
                    .result { margin: 20px 0; padding: 10px; background-color: #f0f0f0; }
                </style>
            </head>
            <body>
                <h1>Тестовый аукцион №12345</h1>
                <div class="status">{{ status }}</div>
                <div class="timer" id="timer">{{ timer_text }}</div>
                
                <form method="POST" action="/submit_bid">
                    <button type="submit" class="bid-button" {{ button_disabled }}>
                        Подать предложение +1 шаг
                    </button>
                </form>
                
                {% if bid_time %}
                <div class="result">
                    <h3>Результат теста:</h3>
                    <p>Время подачи ставки: {{ bid_time }} сек после начала</p>
                    <p>Реакция: {{ reaction_time }} мс</p>
                </div>
                {% endif %}
                
                <script>
                    function updateTimer() {
                        fetch('/get_timer')
                            .then(response => response.json())
                            .then(data => {
                                document.getElementById('timer').textContent = data.timer_text;
                                if (data.auction_started) {
                                    location.reload();
                                }
                            });
                    }
                    
                    setInterval(updateTimer, 100);
                </script>
            </body>
            </html>
            """
            
            return render_template_string(
                html_template,
                status=status,
                timer_text=timer_text,
                button_disabled=button_disabled,
                bid_time=request.args.get('bid_time'),
                reaction_time=request.args.get('reaction_time')
            )
        
        @self.app.route('/submit_bid', methods=['POST'])
        def submit_bid():
            """Обработка подачи ставки"""
            if self.auction_start_time and datetime.now() >= self.auction_start_time:
                self.bid_received_time = datetime.now()
                reaction_time = (self.bid_received_time - self.auction_start_time).total_seconds() * 1000
                
                return f"""
                <html>
                <body>
                    <h2>Ставка принята!</h2>
                    <p>Время реакции: {reaction_time:.2f} мс</p>
                    <a href="/?bid_time={(self.bid_received_time - self.auction_start_time).total_seconds():.3f}&reaction_time={reaction_time:.2f}">Назад</a>
                </body>
                </html>
                """
            else:
                return "Аукцион еще не начался!", 400
        
        @self.app.route('/get_timer')
        def get_timer():
            """API для получения статуса таймера"""
            current_time = datetime.now()
            
            if self.auction_start_time and current_time >= self.auction_start_time:
                return {
                    'timer_text': '00:00',
                    'auction_started': True
                }
            elif self.auction_start_time:
                time_left = (self.auction_start_time - current_time).total_seconds()
                timer_text = f"{int(time_left):02d}:{int((time_left % 1) * 100):02d}"
                return {
                    'timer_text': timer_text,
                    'auction_started': False
                }
            else:
                return {
                    'timer_text': '--:--',
                    'auction_started': False
                }
        
        @self.app.route('/start_auction_in/<int:seconds>')
        def start_auction_in(seconds):
            """Запуск аукциона через указанное количество секунд"""
            self.auction_start_time = datetime.now() + timedelta(seconds=seconds)
            self.bid_received_time = None
            return f"Аукцион начнется в {self.auction_start_time.strftime('%H:%M:%S.%f')[:-3]}"
        
        @self.app.route('/reset')
        def reset():
            """Сброс симулятора"""
            self.auction_start_time = None
            self.bid_received_time = None
            return "Симулятор сброшен"
    
    def run(self):
        """Запуск симулятора"""
        print(f"🚀 Запуск симулятора аукциона на http://localhost:{self.port}")
        print("Доступные команды:")
        print("  /start_auction_in/5 - начать аукцион через 5 секунд")
        print("  /reset - сбросить симулятор")
        
        # Автоматическое открытие в браузере
        webbrowser.open(f"http://localhost:{self.port}")
        
        self.app.run(port=self.port, debug=False)


def test_speed_with_simulator():
    """Тестирование скорости с симулятором"""
    simulator = AuctionSimulator()
    
    # Запуск симулятора в отдельном потоке
    simulator_thread = threading.Thread(target=simulator.run)
    simulator_thread.daemon = True
    simulator_thread.start()
    
    print("Симулятор запущен. Настройте бота на http://localhost:5000")
    print("Для начала теста выполните: http://localhost:5000/start_auction_in/10")


if __name__ == "__main__":
    test_speed_with_simulator()
