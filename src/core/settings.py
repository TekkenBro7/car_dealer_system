import os
from datetime import timedelta
from pathlib import Path

import environ

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

INSTALLED_APPS = [
    "drf_yasg",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "users",
    "dealerships",
    "cars",
    "suppliers",
    "offers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/{env("REDIS_DB")}',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INTERNAL_IPS = [
    "127.0.0.1",
]

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
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
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

BACKEND_URL = env("BACKEND_URL")

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

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT Auth header. Example: "Bearer <access token>"',
        }
    },
    "USE_SESSION_AUTH": False,
}
