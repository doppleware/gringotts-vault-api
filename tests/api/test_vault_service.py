import json

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from gringotts.models.vault import Vault
from gringotts.models.vault_key import VaultKey
from gringotts.models.vault_owner import VaultOwner

pytestmark = pytest.mark.anyio


@pytest.mark.asyncio
async def test_trying_to_authenticate_with_nonexisting_owner_fails(anyio_backend, client: AsyncClient,
                                                                   vault_owner: VaultOwner, vault_key: VaultKey):
    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": 'gargamel',
                                                                         "vault_number": vault_owner.vault_id,
                                                                         "vault_key": vault_key.key})
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_trying_to_authenticate_with_valid_owner_returns_token(anyio_backend, client: AsyncClient,
                                                                     vault_owner: VaultOwner, vault_key: VaultKey):
    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                         "vault_number": vault_owner.vault_id,
                                                                         "vault_key": vault_key.key})

    assert response.status_code == HTTP_200_OK
    response_json = json.loads(response.text)
    assert response_json['access_token']


@pytest.mark.asyncio
async def test_trying_to_authenticate_with_valid_owner_but_wrong_safe_number_fails(anyio_backend, client: AsyncClient,
                                                                                   vault_owner: VaultOwner,
                                                                                   vault_key: VaultKey):
    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                         "vault_number": 777,
                                                                         "vault_key": vault_key.key})

    assert response.status_code == HTTP_401_UNAUTHORIZED



@pytest.mark.asyncio
async def test_cannot_access_vault_that_doesnt_belong_to_owner(anyio_backend, client: AsyncClient,
                                                               vault_owner: VaultOwner, another_vault_owner: VaultOwner,
                                                               vault_key: VaultKey):
    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                         "vault_number": another_vault_owner.vault_id,
                                                                         "vault_key": vault_key.key})

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_authentication_fails_if_owner_provides_wrong_vault_number(anyio_backend, client: AsyncClient,
                                                                         vault_owner: VaultOwner, vault_key:VaultKey):

    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                         "vault_number": '999',
                                                                         "vault_key": vault_key.key})

    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_authentication_fails_if_owner_provides_wrong_vault_number(anyio_backend, client: AsyncClient,
                                                                         vault_owner: VaultOwner, vault: Vault):

    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                         "vault_number": vault.vault_number,
                                                                         "vault_key": 'randomkey'})

    assert response.status_code == HTTP_401_UNAUTHORIZED



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


async def _create_vault(db_session, number, vault_key):
    async with db_session as session:
        session: AsyncSession
        new_vault = Vault(vault_number=number, vault_key_id=vault_key.key)
        session.add(new_vault)
        await session.commit()
    return new_vault

