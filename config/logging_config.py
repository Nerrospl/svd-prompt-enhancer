"""
config/logging_config.py
Konfiguracja loggingu aplikacji
"""

import logging
from pathlib import Path
from config.constants import LOG_DIR, LOG_FORMAT, LOG_LEVEL


def setup_logging():
    """Setup logging do pliku i console"""
    
    log_file = LOG_DIR / "app.log"
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging configured – file: {log_file}")