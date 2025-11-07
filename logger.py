import logging
import os

#creating logs directory

os.makedirs("logs",exist_ok=True)

LOG_FILE = "logs/app.log"

logging.basicConfig(
    level = logging.INFO,
    format  = "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers = [
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) ->logging.Logger:
    return logging.getLogger(name)