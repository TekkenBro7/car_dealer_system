import os
from pathlib import Path

import environ


class BaseConfig:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    env = environ.Env(
        DEBUG=(bool, False),
        ALLOWED_HOSTS=(list, []),
        DB_PORT=(int, 5432),
        EMAIL_PORT=(int, 587),
        EMAIL_USE_TLS=(bool, True),
        JWT_ACCESS_TOKEN_LIFETIME_SECONDS=(int, 3600),
        JWT_REFRESH_TOKEN_LIFETIME_SECONDS=(int, 86400),
        JWT_ROTATE_REFRESH_TOKENS=(bool, True),
        JWT_BLACKLIST_AFTER_ROTATION=(bool, True),
        JWT_UPDATE_LAST_LOGIN=(bool, True),
    )

    environ.Env.read_env(os.path.join(BASE_DIR, ".env"), overwrite=True)

    SECRET_KEY = env("SECRET_KEY")
    DEBUG = env("DEBUG")
    ALLOWED_HOSTS = env("ALLOWED_HOSTS")
