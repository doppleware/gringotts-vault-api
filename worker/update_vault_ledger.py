import psycopg2
import logging
from datetime import datetime
from opentelemetry import trace

from appraise import Appraisal

from config import get_settings

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def _get_now_time_formatted() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def update_vault_appraisal(appraisal: Appraisal, vault_number: int):
    with tracer.start_as_current_span("updating ledger records with appraise"):
        current_time = _get_now_time_formatted()

        query = f"INSERT INTO gringotts.vault_ledgers (vault_number, last_appraised, sickles, knuts, galleons) " \
                f"VALUES({vault_number},'{current_time}',{appraisal.sickles},{appraisal.knuts},{appraisal.galleons}) " \
                f"ON CONFLICT (vault_number) DO UPDATE SET last_appraised ='{current_time}', " \
                f"sickles={appraisal.sickles}, knuts={appraisal.knuts}, galleons={appraisal.galleons};"

        settings = get_settings()
        logging.debug(
            f'Running query to update the ledger record for {str(vault_number)}: db: {settings.pg_db} user={settings.pg_user} host={settings.pg_host}')
        conn = psycopg2.connect(
            f"dbname={settings.pg_db} user={settings.pg_user} host={settings.pg_host} password={settings.pg_pass}")
        cur = conn.cursor()
        cur.execute(query)
