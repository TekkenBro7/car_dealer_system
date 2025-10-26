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
