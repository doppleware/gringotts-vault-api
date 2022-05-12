
import psycopg2
from appraise import Appraisal

from config import get_settings


def update_vault_appraisal(appraisal :Appraisal, vault_number:int):
    conn = psycopg2.connect(f"dbname={get_settings().pg_db} user={get_settings().pg_user} host={get_settings().pg_host} password={get_settings().pg_pass}")
    cur = conn.cursor()
    query = f"UPDATE gringotts.vault_ledgers SET sickles={appraisal.sickles}, galleons={appraisal.galleons},knuts={appraisal.knuts} WHERE vault_number ='{vault_number}' "
    cur.execute(query)
 