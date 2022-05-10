import os

test_database: str = os.getenv("POSTGRES_TEST_DB", "testdb")
os.environ['POSTGRES_DB'] = test_database
