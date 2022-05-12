from dotenv import load_dotenv
load_dotenv(verbose=True)
import asyncio
import pathlib
import pika, sys, os
from pika.credentials import PlainCredentials
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.pika import PikaInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from config import get_settings
from goblin_worker import goblins_wait_for_work


def main():



    resource = Resource.create(attributes={SERVICE_NAME: 'vault_services'})
    exporter = OTLPSpanExporter(endpoint=get_settings().otlp_exporter_url, insecure=True)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    pika_instrumentation = PikaInstrumentor()
    Psycopg2Instrumentor().instrument()
    cr =PlainCredentials(get_settings().rabbit_user, get_settings().rabbit_pass)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_settings().rabbit_host, credentials=cr))
    channel = connection.channel()
    pika_instrumentation.instrument_channel(channel=channel)
    channel.queue_declare(queue='appraisal_requests')
    goblins_wait_for_work(channel)



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print (e.message)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)