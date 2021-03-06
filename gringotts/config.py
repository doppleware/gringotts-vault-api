import logging
import os
from functools import lru_cache

from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """

    BaseSettings, from Pydantic, validates the data so that when we create an instance of Settings,
     environment and testing will have types of str and bool, respectively.

    Parameters:
    pg_user (str):
    pg_pass (str):
    pg_database: (str):
    pg_test_database: (str):
    asyncpg_url: AnyUrl:
    asyncpg_test_url: AnyUrl:

    Returns:
    instance of Settings

    """

    pg_user: str = os.getenv("POSTGRES_USER", "")
    pg_pass: str = os.getenv("POSTGRES_PASSWORD", "")
    pg_host: str = os.getenv("POSTGRES_HOST", "")
    pg_database: str = os.getenv("POSTGRES_DB", "")
    asyncpg_url: str = f"postgresql+asyncpg://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_database}"

    jwt_secret_key: str = os.getenv("SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("ALGORITHM", "")
    jwt_access_toke_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1)

    rabbit_user: str = os.getenv("RABBITMQ_USER", "")
    rabbit_pass: str = os.getenv("RABBITMQ_PASSWORD", "")
    rabbit_host: str = os.getenv("RABBITMQ_HOST", "")

    appraisal_queue: str = os.getenv("APPRAISAL_QUEUE", "")
    appraisal_routing_key: str = os.getenv("APPRAISAL_ROUTING_KEY", "")

    otlp_exporter_url: str = os.getenv("OTLP_EXPORTER_URL", "")

    muggle_exchange_api: str = os.getenv("MUGGLE_EXCHANGE_API", "")


@lru_cache()
def get_settings():
    logger.info("Loading config settings from the environment...")
    return Settings()
