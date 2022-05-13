import datetime

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from gringotts.models.vault_key import VaultKey
from gringotts.models.vault import Vault
from gringotts.models.vault_owner import VaultOwner
from gringotts.models.vault_ledger import VaultLedger


@pytest_asyncio.fixture
async def another_vault_owner(db_session, another_vault) -> VaultOwner:
    merlin = await _create_vault_owner(db_session, vault=another_vault, username='Gandalf', name='Gandalf the Gray')

    return merlin

@pytest_asyncio.fixture
async def another_vault(db_session, another_vault_key: VaultKey) -> Vault:
    new_vault = await _create_vault(db_session, number=22222223, vault_key=another_vault_key)

    return new_vault


@pytest_asyncio.fixture
async def another_vault_key(db_session) -> VaultKey:
    key = await _create_vault_key(db_session, key="open")
    return key

@pytest_asyncio.fixture
async def vault_owner(db_session, vault) -> VaultOwner:
    merlin = await _create_vault_owner(db_session, username='merlin', vault=vault, name='Merlin the great')

    return merlin

@pytest_asyncio.fixture
async def vault_ledger(db_session, vault: Vault) -> VaultLedger:
    new_vault = await _create_vault_ledger(db_session, vault.vault_number, 100,1000, 10000)
    return new_vault


@pytest_asyncio.fixture
async def unappraised_ledger(db_session, vault: Vault) -> VaultLedger:
    new_vault = await _create_unappraised_ledger(db_session, vault.vault_number)
    return new_vault

@pytest_asyncio.fixture
async def another_vault_ledger(db_session, another_vault: Vault) -> VaultLedger:
    new_vault = await _create_vault_ledger(db_session, another_vault.vault_number, 200,2000, 20000)
    return new_vault


@pytest_asyncio.fixture
async def vault(db_session, vault_key: VaultKey) -> Vault:
    new_vault = await _create_vault(db_session, number=22222222, vault_key=vault_key)
    return new_vault


@pytest_asyncio.fixture
async def vault_key(db_session) -> VaultKey:
    key = await _create_vault_key(db_session, key="sesame")
    return key


async def _create_vault_key(db_session, key:str):
    async with db_session as session:
        session: AsyncSession
        key = VaultKey(key=key)
        session.add(key)
        await session.commit()
    return key


async def _create_vault_owner(db_session, name: str, username: str, vault: Vault):
    async with db_session as session:
        session: AsyncSession
        merlin = VaultOwner(name=name, species=VaultOwner.Species.Human, username=username, vault_id=vault.vault_number)
        session.add(merlin)
        await session.commit()
    return merlin


async def _create_unappraised_ledger(db_session, vault_number:int):
    async with db_session as session:
        session: AsyncSession
        ledger = VaultLedger(vault_number=vault_number)
        session.add(ledger)
        await session.commit()
    return ledger


async def _create_vault_ledger(db_session, vault_number:int, galleons:int, sickles:int, knuts:int):
    async with db_session as session:
        session: AsyncSession
        ledger = VaultLedger(vault_number=vault_number)
        ledger.galleons=galleons
        ledger.knuts=knuts
        ledger.sickles=sickles
        ledger.last_appraised=datetime.datetime.now()
        session.add(ledger)
        await session.commit()
    return ledger


async def _create_vault(db_session, number, vault_key):
    async with db_session as session:
        session: AsyncSession
        new_vault = Vault(vault_number=number, vault_key_id=vault_key.key)
        session.add(new_vault)
        await session.commit()
    return new_vault
