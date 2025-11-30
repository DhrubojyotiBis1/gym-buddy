import logging
from config import Config

_LOGGER_NAME = "direct_chat"

def get_logger(name: str = _LOGGER_NAME) -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(Config.LOG_FORMATER, datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger

logger = get_logger()