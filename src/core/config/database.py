from core.config.base import BaseConfig


class DatabaseConfig:
    env = BaseConfig.env

    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE"),
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": env("POSTGRES_PORT"),
        }
    }
