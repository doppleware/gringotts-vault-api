import asyncio
from random import randint
import time
import psycopg2
import logging
from datetime import datetime
from opentelemetry import trace
import threading

from pydantic import BaseModel 

from worker.config import get_settings

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

lock = threading.Lock()

def _get_now_time_formatted() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Appraisal(BaseModel):
    sickles: int
    galleons: int
    knuts: int


def go_appraise_vault(ch, method, properties, body):
    with tracer.start_as_current_span("handling appraisal request for vault"):
        # Its not that urgent
        time.sleep(1)

        vault_id = body.decode('utf-8')
        logger.debug(f'received request to appraise vault {vault_id}')
        appraisal: Appraisal = _appraise()
        _update_vault_appraisal(appraisal=appraisal, vault_number=vault_id)

def _appraise() -> Appraisal:
    # Work takes time
    time.sleep(randint(0, 5))
    return Appraisal(sickles=randint(0, 10000),
                     galleons=randint(0, 1000),
                     knuts=randint(0, 100000)
                     )

def _update_vault_appraisal(appraisal: Appraisal, vault_number: int):
    with tracer.start_as_current_span("updating ledger records with appraise"):
        try:
            lock.acquire()
            current_time = _get_now_time_formatted()

            query = f"INSERT INTO gringotts.vault_ledgers (vault_number, last_appraised, sickles, knuts, galleons) " \
                    f"VALUES({vault_number},'{current_time}',{appraisal.sickles},{appraisal.knuts},{appraisal.galleons}) " \
                    f"ON CONFLICT (vault_number) DO UPDATE SET last_appraised ='{current_time}', " \
                    f"sickles={appraisal.sickles}, knuts={appraisal.knuts}, galleons={appraisal.galleons};"

            settings = get_settings()
            logging.error(
                f'Running query to update the ledger record for {str(vault_number)}: db: {settings.pg_db} user={settings.pg_user} host={settings.pg_host}')
            conn = psycopg2.connect(
                f"dbname={settings.pg_db} user={settings.pg_user} host={settings.pg_host} password={settings.pg_pass}")
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
        finally:
            lock.release()