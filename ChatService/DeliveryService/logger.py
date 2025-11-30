import logging
from logging.config import dictConfig
from config import Config

def get_logger():
    logger = logging.getLogger("delivery")
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(Config.LOG_FORMATTER)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    return logger

def setup_logging():
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': Config.LOG_FORMATTER,
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    })


logger = get_logger()