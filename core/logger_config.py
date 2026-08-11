import logging
import os

LOG_FILE = "house_gamified.log"

def setup_logging():
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return root_logger
    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    root_logger.info("Sistema de registro de HouseGamified iniciado.")
    return root_logger

setup_logging()
def get_logger(name):
    return logging.getLogger(name)
