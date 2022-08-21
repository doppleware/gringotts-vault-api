from dotenv import load_dotenv
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from worker.queueing import create_queue_channel
import sys, os
import logging
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.digma import DigmaConfiguration
from worker.config import get_settings
from worker.goblin_worker import GoblinWorkers

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)


def main():
    settings = get_settings()

    setup_observability(settings)
    channel = create_queue_channel(settings)
    GoblinWorkers(channel=channel).goblins_wait_for_work()


def setup_observability(settings):
    resource = Resource.create(attributes={SERVICE_NAME: 'goblin_worker'})
    resource = DigmaConfiguration().trace_this_package()\
                    .resource.merge(resource)
    exporter = OTLPSpanExporter(endpoint=settings.otlp_exporter_url, insecure=True)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    Psycopg2Instrumentor().instrument()
    LoggingInstrumentor().instrument(set_logging_format=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print (str(e))
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)