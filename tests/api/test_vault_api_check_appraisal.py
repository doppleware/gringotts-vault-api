import json
import logging

import pika
import pytest
from httpx import AsyncClient
from pika import PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_410_GONE, HTTP_201_CREATED

from gringotts.config import get_settings

pytestmark = pytest.mark.anyio
from tests.api.domain_fixtures import  *


class GoblinWorker:
    def __init__(self, channel: BlockingChannel) -> None:
        self.appraise_request_received = False
        self.vault_id_received = None
        channel.queue_declare(get_settings().appraisal_queue)
        self.channel=channel

    def consume(self):
        self.channel.basic_consume(queue=get_settings().appraisal_queue, on_message_callback=self.go_appraise_vault,
                                   auto_ack=True)
        self.channel._process_data_events(4)

    def go_appraise_vault(self, ch, method, properties, body):
        self.appraise_request_received = True
        self.vault_id_received = body.decode('utf-8')

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

@pytest.mark.asyncio
async def test_returns_missing_if_not_appraised(anyio_backend,
                                                client: AsyncClient,
                                                vault_owner: VaultOwner,
                                                vault_key: VaultKey,
                                                unappraised_ledger: VaultLedger):

    params = {"vault_id": vault_owner.vault_id, "muggle_currency_code" : "usd"}
    headers = await _login_for_token(client, vault_key, vault_owner)
    response = await client.get("/gringotts/vaults/appraisal", params=params, headers=headers)

    assert response.status_code == HTTP_410_GONE


@pytest.mark.asyncio
async def test_request_vault_appraisal(anyio_backend,
                                       client: AsyncClient,
                                       vault_owner: VaultOwner,
                                       vault_key: VaultKey,
                                       unappraised_ledger: VaultLedger,
                                       goblin_worker_consumer: GoblinWorker):

    headers = await _login_for_token(client, vault_key, vault_owner)

    response = await client.post("/gringotts/vaults/appraise",  headers=headers,
                                 json={"vault_id": vault_owner.vault_id})

    assert response.status_code == HTTP_201_CREATED

    goblin_worker_consumer.consume()

    assert goblin_worker_consumer.appraise_request_received

    assert  goblin_worker_consumer.vault_id_received == str(vault_owner.vault_id)



async def _login_for_token(client, vault_key, vault_owner):
    response = await client.post("/gringotts/vaults/authenticate", json={"vault_owner": vault_owner.username,
                                                                         "vault_number": vault_owner.vault_id,
                                                                         "vault_key": vault_key.key})
    response_json = json.loads(response.text)
    headers = {"Authorization": f"Bearer {response_json['access_token']}"}
    return headers

@pytest_asyncio.fixture
async def goblin_worker_consumer(consumer_channel: BlockingChannel) -> GoblinWorker:
    return GoblinWorker(channel=consumer_channel)

@pytest_asyncio.fixture
async def consumer_channel() -> BlockingChannel:
    while True:
        try:
            cr = PlainCredentials(get_settings().rabbit_user, get_settings().rabbit_pass)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=get_settings().rabbit_host, credentials=cr))
            return connection.channel()
        except Exception as e:
            logging.error(str(e))



