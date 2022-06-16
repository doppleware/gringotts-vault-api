import asyncio
import json

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from tests.gringotts.api.domain_fixtures import *

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


@pytest.mark.asyncio
async def test_trying_to_authenticate_multiple_timeswith_valid_owner_returns_token(anyio_backend, client: AsyncClient,
                                                                 vault_owner: VaultOwner, vault_key: VaultKey):
    promises = []

    for i in range(10):
        respons_callback = client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                       "vault_number": vault_owner.vault_id,
                                                                       "vault_key": vault_key.key})
        promises.append(respons_callback)

    responses = await asyncio.gather(*promises)

    for response in responses:

        assert response.status_code == HTTP_200_OK
        response_json = json.loads(response.text)
        assert response_json['access_token']


