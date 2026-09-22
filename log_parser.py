import logging
import os

# Настройка логирования
logging.basicConfig(
    filename='app_actions.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

def log_action(action_type, details):
    """Логирует действие пользователя или системы"""
    msg = f"ACTION: {action_type} | DETAILS: {details}"
    logging.info(msg)

def parse_logs():
    """Парсит файл логов и возвращает последние события"""
    log_file = 'app_actions.log'
    if not os.path.exists(log_file):
        return ["Логи пока пусты."]
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Возвращаем последние 20 записей
    return [line.strip() for line in lines[-20:]]