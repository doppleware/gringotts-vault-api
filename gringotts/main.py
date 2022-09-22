import logging
from fastapi import FastAPI
from opentelemetry.instrumentation.digma import DigmaConfiguration
from opentelemetry.instrumentation.digma.fastapi import DigmaFastAPIInstrumentor

from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from gringotts.api.vault_service import router as vault_router
from gringotts.config import get_settings
from gringotts.database import engine
from gringotts.models.base import Base
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace

from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)

app = FastAPI(title="Gringotts Vault API", version="0.3")

app.include_router(vault_router)

resource = Resource.create(attributes={SERVICE_NAME: 'vault_service'})
resource = DigmaConfiguration().trace_this_package()\
                    .set_environment("Dev").resource.merge(resource)
exporter = OTLPSpanExporter(endpoint=get_settings().otlp_exporter_url, insecure=True)
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

Instrumentator().instrument(app).expose(app)


RequestsInstrumentor().instrument()
LoggingInstrumentor().instrument(set_logging_format=True)
AsyncPGInstrumentor().instrument()
# Exclude URLs that are not a part of the core app like /info
FastAPIInstrumentor().instrument_app(app, excluded_urls="^(?!http[s]?://.*/gringotts).*$")
DigmaFastAPIInstrumentor().instrument_app(app)

HTTPXClientInstrumentor().instrument()

tracer = trace.get_tracer(__name__)


async def start_db():
    async with engine.begin() as conn:
        conn = await conn.execution_options(schema_translate_map={None: "gringotts"})
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await start_db()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
