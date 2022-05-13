from dotenv import load_dotenv

from queueing import create_queue_channel
load_dotenv(verbose=True)
import pathlib
import pika, sys, os
import logging
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from config import get_settings
from goblin_worker import goblins_wait_for_work

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

def main():

    settings = get_settings()

    resource = Resource.create(attributes={SERVICE_NAME: 'vault_services'})
    exporter = OTLPSpanExporter(endpoint=settings.otlp_exporter_url, insecure=True)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    Psycopg2Instrumentor().instrument()
    channel = create_queue_channel(settings)
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