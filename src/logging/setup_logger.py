import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)
    
    if logger.hasHandlers():
        return
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)