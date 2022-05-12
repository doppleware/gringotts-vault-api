# Dependency
import pika
from opentelemetry.instrumentation.pika import PikaInstrumentor
from pika import PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel


def get_channel(queue: str ) -> BlockingChannel:

    cr = PlainCredentials('admin', 'admin')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=cr))
    channel = connection.channel()
    channel.queue_declare(queue=queue)

    pika_instrumentation = PikaInstrumentor()
    pika_instrumentation.instrument_channel(channel=channel)

