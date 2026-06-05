import logging
import os

def setup_streamlit_logger():
    LOGGER_DOC = "logs"
    os.makedirs(LOGGER_DOC, exist_ok= True)

    LOGGER_CARPET = os.path.join(LOGGER_DOC, "streamlit_client")

    logger = logging.getLogger("streamlit_client")
    logger.setLevel(logging.DEBUG)

    # File Handler
    file_handler = logging.FileHandler(LOGGER_CARPET, mode="a")
    file_handler.setLevel(logging.DEBUG)

    # Formato
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Agregar handler solo si no existe
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger














