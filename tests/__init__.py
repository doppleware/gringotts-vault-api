import os

test_database: str = os.getenv("POSTGRES_TEST_DB", "testdb")
os.environ['POSTGRES_DB'] = test_database
test_appraisal_queue: str = os.getenv("APPRAISAL_QUEUE", "test_appraisal_requests")
os.environ['APPRAISAL_ROUTING_KEY'] = test_appraisal_queue
test_routing_key: str = os.getenv("APPRAISAL_ROUTING_KEY", "test_appraisal_requests")
os.environ['APPRAISAL_ROUTING_KEY'] = test_routing_key
