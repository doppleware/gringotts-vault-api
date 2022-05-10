import asyncio

import pika
from fastapi import APIRouter, Depends, status
from opentelemetry import trace
from opentelemetry.instrumentation.pika import PikaInstrumentor
from pika.credentials import PlainCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import PlainTextResponse

from gringotts.domain.vault_authorization import validate_vault_owner_and_key, CreatureNotAuthenticatedException
from gringotts.authentication.keysmith import create_access_token
from gringotts.database import get_db
from gringotts.schemas.authentication import AuthenticationRequest, TokenResponse
from gringotts.schemas.vault_balance import VaultBalanceResponse

router = APIRouter(prefix="/v1/gringotts/vaults")
tracer = trace.get_tracer(__name__)


@router.post("/authenticate", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def authenticate_key(payload: AuthenticationRequest, db_session: AsyncSession = Depends(get_db)):

    try:
        await validate_vault_owner_and_key(db_session=db_session, request=payload)

    except CreatureNotAuthenticatedException:
        error_json = {"Unauthorized": f"User does not have permissions to access vault : {payload.vault_owner}"}
        return PlainTextResponse(str(error_json), status_code=status.HTTP_401_UNAUTHORIZED)

    token = create_access_token(payload.__dict__)

    token_response = TokenResponse(access_token=token,
                                   token_type='bearer')
    return token_response


    # with tracer.start_as_current_span("sending to central repo"):
    #     cr =PlainCredentials('admin', 'admin')
    #     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=cr))
    #     channel = connection.channel()
    #
    #     channel.queue_declare(queue='moneytransfersqueue')
    #
    #     pika_instrumentation = PikaInstrumentor()
    #     pika_instrumentation.instrument_channel(channel=channel)
    #     channel.basic_publish(exchange='', routing_key='moneytransfersqueue', body="transfer")


@router.get("/balance", response_model=VaultBalanceResponse, status_code=status.HTTP_200_OK)
async def check_balance(db_session: AsyncSession = Depends(get_db)):
    pass

@router.post("/transfer", response_model=VaultBalanceResponse, status_code=status.HTTP_200_OK)
async def transfer_to_vault(db_session: AsyncSession = Depends(get_db)):
    pass
