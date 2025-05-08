# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_file=None):
    logger = logging.getLogger("beerus")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')  # Simple, clean output

    if logger.hasHandlers():
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)  # Handle current dir
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            print(f"[DEBUG] Logging to {log_file}")
        except Exception as e:
            print(f"[DEBUG] Can't set up log file {log_file}: {e}")
            logger.warning(f"Log file setup failed: {e}")

    return logger