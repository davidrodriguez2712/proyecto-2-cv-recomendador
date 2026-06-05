import logging
from logging.handlers import RotatingFileHandler
import os

# Crear carpeta de logs
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok= True)

LOG_FILE = os.path.join(LOGS_DIR, "backend.log")

def setup_backend_logger():
    logger = logging.getLogger("backend")
    logger.setLevel(logging.DEBUG)

    # Eliminar handlers colocados por defecto en uvicorn
    logger.handlers.clear()

    # -- File Handler rotativo ---
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes= 5_000_000,
        backupCount= 5,
        encoding= "utf-8"
    )

    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    ))
    file_handler.setLevel(logging.DEBUG)

    # Consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s - %(message)s"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger







