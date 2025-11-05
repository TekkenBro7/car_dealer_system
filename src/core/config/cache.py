from core.config.base import BaseConfig


class CacheConfig:
    env = BaseConfig.env

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/{env("REDIS_DB")}',
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
    CACHE_TIMEOUT = 60 * 10
    NO_CACHE_PATHS = [
        "/api/auth/verify/",
        "/api/auth/confirm-email/",
        "/api/auth/confirm-username/",
        "/admin/",
    ]
