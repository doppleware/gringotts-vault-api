
import psycopg2
import logging
from appraise import Appraisal

from config import get_settings


def update_vault_appraisal(appraisal :Appraisal, vault_number:int):
    settings = get_settings()
    logging.debug('Connecting to pg: db: {settings.pg_db} user={settings.pg_user} host={settings.pg_host} password={settings.pg_pass}')
    conn = psycopg2.connect(f"dbname={settings.pg_db} user={settings.pg_user} host={settings.pg_host} password={settings.pg_pass}")
    cur = conn.cursor()
    query = f"UPDATE gringotts.vault_ledgers SET sickles={appraisal.sickles}, galleons={appraisal.galleons},knuts={appraisal.knuts} WHERE vault_number ='{vault_number}' "
    cur.execute(query)
 