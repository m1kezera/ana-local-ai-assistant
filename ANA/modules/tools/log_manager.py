import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "ana_debug.log")

def configurar_logger(tamanho_max_mb=2, backups=5):
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Evita handlers duplicados
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=tamanho_max_mb * 1024 * 1024,
        backupCount=backups,
        encoding="utf-8"
    )
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
