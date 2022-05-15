# Gringotts Vault API
![language](https://img.shields.io/badge/language-python-blue?style)
[![Integration Tests](https://github.com/doppleware/gringotts-vault-api/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/doppleware/gringotts-vault-api/actions/workflows/build-and-test.yml)
[![license](https://img.shields.io/github/license/doppleware/gringotts-vault-api)](https://github.com/doppleware/gringotts-vault-api/blob/main/LICENSE)

<p align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Gringotts%2C_Harry_Potter_Studio_Tour_%2848538071011%29.jpg/1597px-Gringotts%2C_Harry_Potter_Studio_Tour_%2848538071011%29.jpg?20210516121542" 
width="600" height="400">
</p>

This is an example on integrating [FastAPI](https://fastapi.tiangolo.com/) and additional libraries with OpenTelemetry and
common tracing tools. The goal is to create more realistic scenarios (if one could say that about a fantasy setting) 
in terms of an application that goes beyond 'simple CRUD' and can demonstrate the value of using distributed tracing in the 
development day to day.  It should be disclaimed and pointed out that this does not purport to be in any way a 'go-to'
architecture - please don't use it as such! It is intended to examine different architectural problems and how we can 
use observability to solve them.

This example is based on a [great repo](https://github.com/grillazz/fastapi-sqlalchemy-asyncpg) by @grillazz from which 
it was also original forked.

The fully instrumented stack includes:
- [SQLAlchemy](https://www.sqlalchemy.org/) ORM
- PostgreSQL via [asyncpg](https://github.com/MagicStack/asyncpg) 
- Async HTTP via [httpx](https://www.python-httpx.org/) we will use it to connect to a mock site created via [mockapi](https://mockapi.io/)
- RabbitMQ queuing via [pika](https://github.com/pika/pika)

From the tracing stack side we'll use:
- [Jaeger](https://www.jaegertracing.io/) for distributed tracing 
- [Prometheus](https://prometheus.io/) for metrics (TBD still WIP)
- [Digma](https://github.com/digma-ai/digma) for getting observability insights back into the code.

### Prerequisites

1. [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/install/) (not a hard requirement, but makes woking with this example easier)
2. Python 3.8+ 
3. [vsCode](https://code.visualstudio.com/) - For some aspects of developer observability
4. Clone or download the repo 


### Up and running in five steps

#### 1. Start the observability stack:
```commandline
docker compose -f ./observability/digma-cf/docker-compose.digma.yml up -d
docker compose -f ./observability/tracing/docker-compose.trace.yml up -d
```
#### 2. Start the Gringotts API application, including all services and background 'Goblin worker' process

```commandline
docker compose --profile standalone -f docker-compose.yml -f docker-compose.override.standalone.yml up -d
```

#### 3. Seed with sample data
This will import in some Wizards from a data source I 
found [online](https://www.kaggle.com/datasets/gulsahdemiryurek/harry-potter-dataset),
to make it a little easier to work with the API 
```commandline
PYTHONPATH=. python ./tests/seed/seed_data.py
```

#### 4. Generate some activity to observe
Go to the API documentation page at http://localhost:8283/docs and login using the authenticate button.

<img width="1473" alt="image" src="https://user-images.githubusercontent.com/93863/168254302-c9f9a7bd-2c33-45fc-b5e8-2efa8e62e362.png">


Since we populated some data you can use the following details:
`username`: hpotter `password`: griffindoor

Notice that it takes some time to process, we'll look into that in a sec.

#### 5. Install the IDE Extension

Install the [Digma extension](https://marketplace.visualstudio.com/items?itemName=digma.digma) on your local IDE.
We'll use Digma to demonstrate continuous feedback.

### Seeing the tracing data

1. Open http://localhost:16686 to access the Jaege instance. By now you should already have some data to look at.
<img width="1726" alt="image" src="https://user-images.githubusercontent.com/93863/168373811-8261c479-e052-4704-aaaa-671e93b49e01.png">

2. Upon installing the [Digma extension](https://marketplace.visualstudio.com/items?itemName=digma.digma) open your vscode and select the Digma icon to see information in the context of the code.



### Installing requirements locally

Create a separate python env for the worker and gringotts folders.
For each environment install the local requirements.txt file.

For example, using virtualenv.
```commandline
cd gringotts
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

#### Issues with psycopg2 and M1 Macbooks. 
I had an issue with this requirement on my local development laptop. 
I had to manually install openssl and then install via pip after setting these environment variables:
```
LDFLAGS="-I/opt/homebrew/opt/openssl@3/include -L/opt/homebrew/opt/openssl@3/lib" pip install psycopg2-binary
```
The solution to this known issue is posted in several places including [here](https://stackoverflow.com/questions/66777470/psycopg2-installed-on-m1-running-macos-big-sur-but-unable-to-run-local-server)

### Development mode
To simply run the backend services (Postgres, RabbitMQ) to develop locally from the IDE, run:
```commandline
docker compose --profile develop -f docker-compose.yml -f docker-compose.override.develop.yml up -d
```

### Run automated tests 

To run the tests via docker compose, use the 
```commandline
 docker compose --profile test -f docker-compose.yml -f docker-compose.override.test.yml up --abort-on-container-exit --attach gt-vault-api
 ```

To run the tests with some seeded data to see how the system behaves with data in place, use:

```commandline
PYTEST_ARGUMENTS="--seed-data true" docker compose --profile test -f docker-compose.yml -f docker-compose.override.test.yml up --abort-on-container-exit --attach gt-vault-api --abort-on-container-exit
 ```
 
 <img width="1028" alt="image" src="https://user-images.githubusercontent.com/93863/168214621-df229754-c0e5-460f-8dc9-ce4c4694df97.png">


