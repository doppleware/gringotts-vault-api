import asyncio

from opentelemetry import trace
from pika.adapters.blocking_connection import BlockingChannel
import psycopg2
from appraise import Appraisal, appraise

from config import get_settings
from update_vault_ledger import update_vault_appraisal

tracer = trace.get_tracer(__name__)


def go_appraise_vault(ch, method, properties, body):
    with tracer.start_as_current_span("handling appraisal request for vault"):
        # Its not that urgent
        asyncio.sleep(1)
        appraisal: Appraisal = appraise()
        update_vault_appraisal(appraisal=appraisal, vault_number=body.decode('utf-8'))

def goblins_wait_for_work(channel: BlockingChannel):
    channel.basic_consume(queue='appraisal_requests', on_message_callback=go_appraise_vault, auto_ack=True)
    channel.start_consuming()

