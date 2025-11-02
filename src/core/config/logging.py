from core.config.base import BaseConfig


class LoggingConfig:
    LOG_DIR = BaseConfig.BASE_DIR.parent / "logs"
    LOG_DIR.mkdir(exist_ok=True)

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": LOG_DIR / "debug.log",
                "formatter": "verbose",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    }
