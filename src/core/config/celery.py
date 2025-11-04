from datetime import timedelta

from core.config.base import BaseConfig


class CeleryConfig:
    env = BaseConfig.env

    CELERY_BROKER_URL = (
        f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/{env("CELERY_BROKER_DB")}'
    )
    CELERY_RESULT_BACKEND = (
        f'redis://{env("REDIS_HOST")}:{env("REDIS_PORT")}/{env("CELERY_RESULT_DB")}'
    )
    CELERY_TIMEZONE = "UTC"
    CELERY_TASK_TRACK_STARTED = env("CELERY_TASK_TRACK_STARTED")
    CELERY_TASK_TIME_LIMIT = env("CELERY_TASK_TIME_LIMIT")

    CELERY_BEAT_SCHEDULE = {
        "auto-buy-from-suppliers": {
            "task": "dealerships.tasks.auto_buy_from_suppliers",
            "schedule": timedelta(minutes=10),
        },
        "process-pending-offers": {
            "task": "offers.tasks.process_pending_offers",
            "schedule": timedelta(seconds=15),
        },
    }
