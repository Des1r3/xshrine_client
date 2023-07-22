LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": { 
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s | %(levelname)s     | - %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s | %(levelname)s     | %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        "main": {
            "format": "%(asctime)s | %(levelname)s     |  %(module)s:%(funcName)s:%(lineno)d - %(message)s",
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
        "main": {
            "formatter": "main",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "main": {"handlers": ["main"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}