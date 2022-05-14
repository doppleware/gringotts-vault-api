import logging
import time
from pika.adapters.blocking_connection import BlockingChannel
from config import Settings
from pika.credentials import PlainCredentials
from opentelemetry.instrumentation.pika import PikaInstrumentor
import pika


def create_queue_channel(settings: Settings) -> BlockingChannel:
    pika_instrumentation = PikaInstrumentor()
    cr = PlainCredentials(settings.rabbit_user, settings.rabbit_pass)
    logging.debug(f'Connecting to RabbitMQ: {settings.rabbit_user}/{settings.rabbit_pass}:{settings.rabbit_host}')

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbit_host, credentials=cr))
    channel = connection.channel()
    pika_instrumentation.instrument_channel(channel=channel)
    channel.queue_declare(queue='appraisal_requests')
    return channel
