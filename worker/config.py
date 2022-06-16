from logging import Logger
import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):

    pg_user: str = os.getenv("POSTGRES_USER", "")
    pg_pass: str = os.getenv("POSTGRES_PASSWORD", "")
    pg_host: str = os.getenv("POSTGRES_HOST", "")
    pg_db: str = os.getenv("POSTGRES_DB", "")

    rabbit_user: str = os.getenv("RABBITMQ_USER", "")
    rabbit_pass: str = os.getenv("RABBITMQ_PASSWORD", "")
    rabbit_host: str = os.getenv("RABBITMQ_HOST", "")

    otlp_exporter_url: str = os.getenv("OTLP_EXPORTER_URL", "")
    
    appraisal_queue: str = os.getenv("APPRAISAL_QUEUE", "")
    appraisal_routing_key: str = os.getenv("APPRAISAL_ROUTING_KEY", "")

@lru_cache()
def get_settings():
    return Settings()
