"""
Расширенная система логирования
"""
import logging
import os
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Форматтер для JSON логов"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(config):
    """Настройка системы логирования"""
    log_config = config['logging']
    
    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_config['level']))
    
    # Форматеры
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    json_formatter = JSONFormatter()
    
    # File handler (ротация логов)
    file_handler = RotatingFileHandler(
        log_config['log_file'],
        maxBytes=log_config['max_log_size'],
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(simple_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    
    # JSON file handler для машинной обработки
    json_handler = RotatingFileHandler(
        'auction_bot_json.log',
        maxBytes=log_config['max_log_size'],
        backupCount=3,
        encoding='utf-8'
    )
    json_handler.setFormatter(json_formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(json_handler)
    
    return logger
