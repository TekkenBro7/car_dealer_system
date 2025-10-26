from datetime import timedelta

from core.config.base import BaseConfig


class JwtConfig:
    env = BaseConfig.env

    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(
            seconds=env("JWT_ACCESS_TOKEN_LIFETIME_SECONDS")
        ),
        "REFRESH_TOKEN_LIFETIME": timedelta(
            seconds=env("JWT_REFRESH_TOKEN_LIFETIME_SECONDS")
        ),
        "ROTATE_REFRESH_TOKENS": env("JWT_ROTATE_REFRESH_TOKENS"),
        "BLACKLIST_AFTER_ROTATION": env("JWT_BLACKLIST_AFTER_ROTATION"),
        "UPDATE_LAST_LOGIN": env("JWT_UPDATE_LAST_LOGIN"),
    }
