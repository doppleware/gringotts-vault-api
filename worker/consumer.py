import asyncio
import pika, sys, os
from pika.credentials import PlainCredentials
from opentelemetry.instrumentation.pika import PikaInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def main():


    resource = Resource.create(attributes={SERVICE_NAME: 'vault_services'})
    exporter = OTLPSpanExporter(endpoint='localhost:4317', insecure=True)
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    pika_instrumentation = PikaInstrumentor()
    cr =PlainCredentials('admin', 'admin')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=cr))
    channel = connection.channel()
    pika_instrumentation.instrument_channel(channel=channel)

    channel.queue_declare(queue='moneytransfersqueue')

    def callback(ch, method, properties, body):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("processing order"):
            asyncio.sleep(2)
            print(" [x] Received %r" % body)

    channel.basic_consume(queue='moneytransfersqueue', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

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