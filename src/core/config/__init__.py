from core.config.base import BaseConfig
from core.config.cache import CacheConfig
from core.config.celery import CeleryConfig
from core.config.database import DatabaseConfig
from core.config.email import EmailConfig
from core.config.jwt import JwtConfig
from core.config.logging import LoggingConfig
from core.config.swagger import SwaggerConfig


class Config:
    base = BaseConfig
    database = DatabaseConfig
    cache = CacheConfig
    email = EmailConfig
    jwt = JwtConfig
    logging = LoggingConfig
    swagger = SwaggerConfig
    celery = CeleryConfig
