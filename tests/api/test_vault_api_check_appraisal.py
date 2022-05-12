import json

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
import json
from gringotts.models.vault import Vault
from gringotts.models.vault_key import VaultKey
from gringotts.models.vault_owner import VaultOwner

pytestmark = pytest.mark.anyio
from tests.api.domain_fixtures import  *


@pytest.mark.asyncio
async def test_cannot_get_appraisal_if_not_logged_in(anyio_backend,
                                                     client: AsyncClient,
                                                     vault_owner: VaultOwner,
                                                     vault_key: VaultKey):

    params = {"vault_id": vault_owner.vault_id}
    response = await client.get("/gringotts/vaults/appraisal", params=params)
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_can_get_appraisal_if_logged_in(anyio_backend,
                                              client: AsyncClient,
                                              vault_owner: VaultOwner,
                                              vault_key: VaultKey,
                                              vault_ledger: VaultLedger):

    params = {"vault_id": vault_owner.vault_id}
    headers = await _login_for_token(client, vault_key, vault_owner)
    response = await client.get("/gringotts/vaults/appraisal", params=params, headers=headers)
    appraisal = json.loads(response.text)

    assert appraisal["galleons"] == vault_ledger.galleons
    assert appraisal["sickles"] == vault_ledger.sickles
    assert appraisal["knuts"] == vault_ledger.knuts

    assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_cannot_get_appraisal_for_vault_owned_by_another(anyio_backend,
                                                               client: AsyncClient,
                                                               another_vault_owner,
                                                               vault_owner: VaultOwner,
                                                               vault_key: VaultKey,
                                                               another_vault_ledger: VaultLedger,
                                                               vault_ledger: VaultLedger):

    params = {"vault_id": another_vault_owner.vault_id}
    headers = await _login_for_token(client, vault_key, vault_owner)
    response = await client.get("/gringotts/vaults/appraisal", params=params, headers=headers)
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_can_get_appraisal_in_muggle_usd(anyio_backend,
                                               client: AsyncClient,
                                               vault_owner: VaultOwner,
                                               vault_key: VaultKey,
                                               vault_ledger: VaultLedger):

    params = {"vault_id": vault_owner.vault_id, "muggle_currency_code" : "usd"}
    headers = await _login_for_token(client, vault_key, vault_owner)
    response = await client.get("/gringotts/vaults/appraisal", params=params, headers=headers)
    appraisal = json.loads(response.text)

    assert appraisal["galleons"] == vault_ledger.galleons
    assert appraisal["sickles"] == vault_ledger.sickles
    assert appraisal["knuts"] == vault_ledger.knuts

    # Todo, maybe check calculation later
    assert appraisal["muggle_currency_value"]
    assert response.status_code == HTTP_200_OK



async def _login_for_token(client, vault_key, vault_owner):
    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                         "vault_number": vault_owner.vault_id,
                                                                         "vault_key": vault_key.key})
    response_json = json.loads(response.text)
    headers = {"Authorization": f"Bearer {response_json['access_token']}"}
    return headers

