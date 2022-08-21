import asyncio
import logging
import threading
import time
import asyncio
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
logger = logging.getLogger(__name__)
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


async def authorize_vault_owner_vault_access(db_session: AsyncSession, vault_owner_id :str, vault_id: int):

    with tracer.start_as_current_span("Authorize vault owner for access"):
        await asyncio.sleep(10)
        owner = await VaultOwner.find(db_session, vault_owner_id)
        await _ensure_owns_requested_vault(owner, vault_id)


async def authenticate_vault_owner_and_key(db_session: AsyncSession, vault_owner: str, vault_key: str ):
    with tracer.start_as_current_span("Authenticate vault owner and key"):
        # Owner is known
        owner = await _ensure_owner_exists(db_session, vault_owner)

        await _ensure_owner_has_a_vault(owner)

        key = await _ensure_key_matches_records(db_session, vault_key)

        await _ensure_key_matches_owner_vault(db_session, key, owner, vault_key)

        return owner


async def _ensure_owns_requested_vault(owner, vault_id):
    if owner.vault_id != vault_id:
        raise CreatureNotAuthenticatedException(f"Specified vault_id {vault_id} doesn't belong to requestor")


async def _ensure_key_matches_owner_vault(db_session, key, owner, vault_ley):
    # Vault requested is the one that belongs to the requestor
    vault: Vault = await Vault.find(db_session, owner.vault_id)
    if vault.vault_key_id != key:
        raise CreatureNotAuthenticatedException(f"Specified key {vault_ley} doesn't match vault")


async def _ensure_key_matches_records(db_session, vault_key: str):
    key = await _search_for_key_record(db_session, key=vault_key)
    if not key:
        raise CreatureNotAuthenticatedException(f"Specified key record {vault_key} not found!")
    return key


async def _ensure_owner_has_a_vault(owner):
    # Vault requested is the one that belongs to the requestor
    vault_id = owner.vault_id
    if not vault_id:
        raise CreatureNotAuthenticatedException(f"Specified vault_id {vault_id} doesn't exist")
    return vault_id


async def _ensure_owner_exists(db_session, vault_owner:str):
    owner: VaultOwner = await VaultOwner.find(username=vault_owner, db_session=db_session)
    if not owner:
        raise CreatureNotAuthenticatedException(f"Creature {vault_owner} isn't a registered owner")
    return owner


async def _search_for_key_record(db_session: AsyncSession, key: str):
    # Purposely inefficient... job security?
    
    with tracer.start_as_current_span("Retrieiving the key record"):
        vaults = await Vault.all(db_session)
        found_key = None
        for vault in vaults:
            vault: Vault
            vault_key = await VaultKey.find(db_session, vault.vault_key_id)
            if vault_key.key == key:
                found_key = key

        return found_key
