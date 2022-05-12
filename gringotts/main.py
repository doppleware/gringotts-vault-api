from fastapi import FastAPI
from opentelemetry.instrumentation.digma import DigmaConfiguration

from gringotts.api.vault_service import router as vault_router
from gringotts.database import engine
from gringotts.models.base import Base
from gringotts.utils import get_logger
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace

from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = get_logger(__name__)

app = FastAPI(title="Gringotts Vault API", version="0.3")

app.include_router(vault_router)

resource = Resource.create(attributes={SERVICE_NAME: 'vault_service'})
resource = DigmaConfiguration().trace_this_package()\
                    .set_environment("Dev").resource.merge(resource)
exporter = OTLPSpanExporter(endpoint='localhost:4317', insecure=True)
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)


RequestsInstrumentor().instrument()
LoggingInstrumentor().instrument(set_logging_format=True)
AsyncPGInstrumentor().instrument()
FastAPIInstrumentor().instrument_app(app)

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
