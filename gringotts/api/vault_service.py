from typing import Optional

from fastapi import APIRouter, Depends, status, HTTPException
from opentelemetry import trace
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import PlainTextResponse

from gringotts.domain.vault_appraisal import get_latest_vault_appraisal
from gringotts.authentication.keysmith import create_access_token
from gringotts.database import get_db
from gringotts.domain.vault_authorization import validate_vault_owner_and_key, CreatureNotAuthenticatedException, \
    get_owner_access, VaultOwnerAccess
from gringotts.schemas.authentication import AuthenticationRequest, TokenResponse, TokenData
from gringotts.schemas.vault_balance import VaultBalanceResponse

router = APIRouter(prefix="/gringotts/vaults")
tracer = trace.get_tracer(__name__)


@router.post("/authenticate", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def authenticate_vault_key(payload: AuthenticationRequest, db_session: AsyncSession = Depends(get_db)):
    try:
        await validate_vault_owner_and_key(db_session=db_session, request=payload)

    except CreatureNotAuthenticatedException:
        error_json = {"Unauthorized": f"User does not have permissions to access vault : {payload.vault_owner}"}
        return PlainTextResponse(str(error_json), status_code=status.HTTP_401_UNAUTHORIZED)

    token = create_access_token(TokenData(vault_owner=payload.vault_owner).__dict__)

    token_response = TokenResponse(access_token=token,
                                   token_type='bearer')
    return token_response


@router.get("/appraisal", response_model=VaultBalanceResponse, status_code=status.HTTP_200_OK)
async def get_vault_appraisal(vault_id: str, muggle_currency_code: Optional[str] = None,
                              db_session: AsyncSession = Depends(get_db),
                              owner_access: VaultOwnerAccess = Depends(get_owner_access)):
    vault_number = int(vault_id)

    if owner_access.vault_number != vault_number:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have permissions to this vault")

    balance = await get_latest_vault_appraisal(db_session=db_session, vault_number=vault_number, muggle_currency_code=muggle_currency_code)
    return balance


@router.post("/transfer", response_model=VaultBalanceResponse, status_code=status.HTTP_200_OK)
async def transfer_to_vault(db_session: AsyncSession = Depends(get_db)):
    pass
