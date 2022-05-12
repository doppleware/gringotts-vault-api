# Dependency
import pika
from opentelemetry.instrumentation.pika import PikaInstrumentor
from pika import PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel

from gringotts.config import get_settings


def get_channel(queue: str ) -> BlockingChannel:

    cr = PlainCredentials(get_settings().rabbit_user, get_settings().rabbit_pass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_settings().pg_host, credentials=cr))
    channel = connection.channel()
    channel.queue_declare(queue=queue)

    pika_instrumentation = PikaInstrumentor()
    pika_instrumentation.instrument_channel(channel=channel)
    return channel

