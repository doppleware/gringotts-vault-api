from fastapi import Depends
from opentelemetry import trace
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gringotts.authentication.keysmith import decypher_access_token, create_access_token
from gringotts.database import get_db
from gringotts.models.vault import Vault
from gringotts.models.vault_owner import VaultOwner
from gringotts.models.vault_key import VaultKey
from gringotts.schemas.authentication import AuthenticationRequest

tracer = trace.get_tracer(__name__)


class CreatureNotAuthenticatedException(Exception):
    def __init__(self, reason: str):
        self.reason = reason


class VaultOwnerAccess(BaseModel):
    vault_owner: str
    vault_number: int


async def get_owner_access(db_session: AsyncSession = Depends(get_db), token: dict = Depends(decypher_access_token)):
    vault_owner_name = token["vault_owner"]
    vault_owner: VaultOwner = await VaultOwner.find(db_session, username=vault_owner_name)
    return VaultOwnerAccess(vault_owner=vault_owner_name, vault_number=vault_owner.vault_id)


async def create_vault_owner_api_key(vault_owner: VaultOwner):
    return create_access_token({"vault_owner": vault_owner.username})


async def validate_vault_owner_and_key(db_session: AsyncSession, request: AuthenticationRequest):
    with tracer.start_as_current_span("Validating authentication request details match"):
        # Owner is known
        owner: VaultOwner = await VaultOwner.find(username=request.vault_owner, db_session=db_session)
        if not owner:
            raise CreatureNotAuthenticatedException(f"Creature {request.vault_owner} isn't a registered owner")

        # Vault requested is the one that belongs to the requestor
        vault_id = owner.vault_id
        if not vault_id:
            raise CreatureNotAuthenticatedException(f"Specified vault_id {vault_id} doesn't exist")
        if vault_id != request.vault_number:
            raise CreatureNotAuthenticatedException(f"Specified vault_id {vault_id} doesn't belong to requestor")

        key = await search_for_key_record(db_session, key=request.vault_key)
        if not key:
            raise CreatureNotAuthenticatedException(f"Specified key record {request.vault_key} not found!")

        # Vault requested is the one that belongs to the requestor
        vault: Vault = await Vault.find(db_session, request.vault_number)
        if vault.vault_key_id != key:
            raise CreatureNotAuthenticatedException(f"Specified key {request.vault_key} doesn't match vault")


async def search_for_key_record(db_session: AsyncSession, key: str):
    # Purposely inefficient... job security?
    with tracer.start_as_current_span("Retrieiving the key record"):
        keys = await VaultKey.all(db_session)
        found_key = None
        for key_record in keys:
            key_record: VaultKey
            if key_record.key == key:
                found_key = key

        return found_key
