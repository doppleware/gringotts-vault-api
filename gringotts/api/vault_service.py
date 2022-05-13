from typing import Optional

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from opentelemetry import trace
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import PlainTextResponse

from gringotts.domain.vault_appraisal import get_latest_vault_appraisal, LedgerExpiredException, request_vault_appraisal
from gringotts.authentication.keysmith import create_access_token
from gringotts.database import get_db
from gringotts.domain.vault_authorization import authenticate_vault_owner_and_key, CreatureNotAuthenticatedException, \
    get_owner_access, VaultOwnerAccess, authorize_vault_owner_vault_access
from gringotts.schemas.authentication import AuthenticationRequest, TokenResponse, TokenData
from gringotts.schemas.vault_balance import VaultBalanceResponse, VaultAppraisalRequest

router = APIRouter(prefix="/gringotts/vaults")
tracer = trace.get_tracer(__name__)


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def authenticate_form(form_data: OAuth2PasswordRequestForm = Depends(), db_session: AsyncSession = Depends(get_db)):
    try:
        await authenticate_vault_owner_and_key(db_session=db_session,
                                               vault_owner=form_data.username,
                                               vault_key=form_data.password)

    except CreatureNotAuthenticatedException:
        error_json = {"Unauthorized": f"User does not have permissions to access vault : {form_data.username}"}
        return PlainTextResponse(str(error_json), status_code=status.HTTP_401_UNAUTHORIZED)

    token = create_access_token(TokenData(vault_owner=form_data.username).__dict__)

    token_response = TokenResponse(access_token=token,
                                   token_type='bearer')
    return token_response


@router.post("/authenticate", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def authenticate_vault_key(payload: AuthenticationRequest, db_session: AsyncSession = Depends(get_db)):
    try:
        await authenticate_vault_owner_and_key(db_session=db_session,
                                                       vault_owner=payload.vault_owner,
                                                       vault_key=payload.vault_key)
        await authorize_vault_owner_vault_access(db_session, payload.vault_owner, payload.vault_number)

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

    await _ensure_authorized_to_vault(db_session,owner_access, vault_number)

    try:
        balance = await get_latest_vault_appraisal(db_session=db_session, vault_number=vault_number,
                                                   muggle_currency_code=muggle_currency_code)
        return balance
    except LedgerExpiredException:
        raise HTTPException(status_code=status.HTTP_410_GONE,
                            detail="There is no up to date balance, please request a new appraisal")


@router.post("/appraise", response_model=VaultBalanceResponse, status_code=status.HTTP_201_CREATED)
async def get_vault_appraisal(payload: VaultAppraisalRequest,
                              db_session: AsyncSession = Depends(get_db),
                              owner_access: VaultOwnerAccess = Depends(get_owner_access)):

    await _ensure_authorized_to_vault(db_session,owner_access, payload.vault_id)
    await request_vault_appraisal(payload.vault_id)


async def _ensure_authorized_to_vault(db_session, owner_access: VaultOwnerAccess, vault_id):
    try:
        await authorize_vault_owner_vault_access(db_session,owner_access.vault_owner,vault_id)
    except CreatureNotAuthenticatedException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have permissions to this vault")
