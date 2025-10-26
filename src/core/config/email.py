from core.config.base import BaseConfig


class EmailConfig:
    env = BaseConfig.env

    EMAIL_BACKEND = env("EMAIL_BACKEND")
    EMAIL_HOST = env("EMAIL_HOST")
    EMAIL_PORT = env("EMAIL_PORT")
    EMAIL_USE_TLS = env("EMAIL_USE_TLS")
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
    BACKEND_URL = env("BACKEND_URL")
