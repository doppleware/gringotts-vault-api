
import psycopg2
import logging

from opentelemetry import trace

from appraise import Appraisal

from config import get_settings
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def update_vault_appraisal(appraisal :Appraisal, vault_number:int):
    with tracer.start_as_current_span("updating ledger records with appraise"):
        settings = get_settings()
        logging.debug(f'Running query to update the ledger record for {str(vault_number)}: db: {settings.pg_db} user={settings.pg_user} host={settings.pg_host}')
        conn = psycopg2.connect(f"dbname={settings.pg_db} user={settings.pg_user} host={settings.pg_host} password={settings.pg_pass}")
        cur = conn.cursor()
        query = f"UPDATE gringotts.vault_ledgers SET sickles={appraisal.sickles}, galleons={appraisal.galleons},knuts={appraisal.knuts} WHERE vault_number ='{vault_number}' "
        cur.execute(query)
 