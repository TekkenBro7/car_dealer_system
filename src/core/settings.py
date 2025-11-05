from core.config import Config

config = Config()

BASE_DIR = config.base.BASE_DIR
SECRET_KEY = config.base.SECRET_KEY
DEBUG = config.base.DEBUG
ALLOWED_HOSTS = config.base.ALLOWED_HOSTS

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
    "core.middleware.cache_get.CacheGETMiddleware",
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

DATABASES = config.database.DATABASES

CACHES = config.cache.CACHES

SIMPLE_JWT = config.jwt.SIMPLE_JWT

LOGGING = config.logging.LOGGING

SWAGGER_SETTINGS = config.swagger.SWAGGER_SETTINGS

EMAIL_BACKEND = config.email.EMAIL_BACKEND
EMAIL_HOST = config.email.EMAIL_HOST
EMAIL_PORT = config.email.EMAIL_PORT
EMAIL_USE_TLS = config.email.EMAIL_USE_TLS
EMAIL_HOST_USER = config.email.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.email.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = config.email.DEFAULT_FROM_EMAIL

BACKEND_URL = config.email.BACKEND_URL

CELERY_BROKER_URL = config.celery.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = config.celery.CELERY_RESULT_BACKEND
CELERY_TIMEZONE = config.celery.CELERY_TIMEZONE
CELERY_TASK_TRACK_STARTED = config.celery.CELERY_TASK_TRACK_STARTED
CELERY_TASK_TIME_LIMIT = config.celery.CELERY_TASK_TIME_LIMIT
CELERY_BEAT_SCHEDULE = config.celery.CELERY_BEAT_SCHEDULE
