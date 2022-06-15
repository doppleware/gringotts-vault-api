

import threading
import pytest
from worker.config import get_settings

from worker.goblin_worker import GoblinWorkers
from worker.main import setup_observability
from worker.queueing import create_queue_channel
from pika.adapters.blocking_connection import BlockingChannel

@pytest.fixture
def goblin_channel() -> BlockingChannel:
    settings = get_settings()
    return create_queue_channel(settings)

@pytest.fixture()
def goblin_workers_listening(goblin_channel: BlockingChannel):
    
    settings = get_settings()
    setup_observability(settings)
    workers = GoblinWorkers(goblin_channel)
    with workers as worker:
        worker : GoblinWorkers
        thread = threading.Thread(target=worker.goblins_wait_for_work)
        thread.daemon = True
        thread.start()
        yield worker

def test_sending_to_goblin_worker(goblin_channel: BlockingChannel, 
                                  goblin_workers_listening: GoblinWorkers):
    
    settings = get_settings()
    goblin_channel.basic_publish(exchange='', routing_key=settings.appraisal_routing_key, body=str(713))




