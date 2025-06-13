import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging format
log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Create formatter
formatter = logging.Formatter(log_format, date_format)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# File Handler - Rotating file handler to manage log file size
file_handler = RotatingFileHandler(
    filename=f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Create logger for the application
logger = logging.getLogger('forum_search')

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    The logger will inherit the configuration from the root logger.
    """
    return logging.getLogger(f'forum_search.{name}') 