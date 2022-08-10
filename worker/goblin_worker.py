import logging

from opentelemetry import trace
from pika.adapters.blocking_connection import BlockingChannel

from worker.jobs.appraise_vault import go_appraise_vault

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class GoblinWorkers:

    def __init__(self, channel: BlockingChannel) -> None:
        self.channel = channel

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.channel.stop_consuming()

    def goblins_wait_for_work(self):
        logging.error('channel waiting')

        self.channel.basic_consume(queue='appraisal_requests', on_message_callback=go_appraise_vault, auto_ack=True)
        self.channel.start_consuming()

