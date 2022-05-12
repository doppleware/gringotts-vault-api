import json
from enum import Enum
from typing import Dict

from httpx import AsyncClient
from opentelemetry import trace
from sqlalchemy.ext.asyncio import AsyncSession

from gringotts.models.vault_ledger import VaultLedger
from gringotts.schemas.vault_balance import VaultBalanceResponse
tracer = trace.get_tracer(__name__)


class MuggleCurrencies(Enum):
    USD = 1
    GBP = 2
    EUR = 3
    TRY = 4
    JPY = 5


async def get_muggle_exchange_rates(currency_code: str):
    with tracer.start_as_current_span("Retrieving muggle exchange rate from API"):
        async with AsyncClient(
                headers={"Content-Type": "application/json"},
        ) as client:
            response = await client.get(config.get_settings().muggle_exchange_api)
            exchange_rates_list = json.loads(response.text)
            muggle_exchange_rate = \
                next((e for e in exchange_rates_list if e["currency_code"] == currency_code.upper()), None)
            return muggle_exchange_rate


async def get_latest_vault_appraisal(db_session: AsyncSession, vault_number:int, muggle_currency_code: str ):
    with tracer.start_as_current_span("Getting latest appraisal for vault"):

        ledger: VaultLedger = await VaultLedger.find_by_vault_id(db_session, vault_number)
        muggle_money_value = -1
        if muggle_currency_code:
            muggle_money_value = await get_muggle_money_value(ledger,muggle_currency_code.upper())

        return VaultBalanceResponse(vault_number=vault_number, galleons=ledger.galleons,
                                    sickles=ledger.sickles,
                                    knuts=ledger.knuts,
                                    muggle_currency_value=muggle_money_value,
                                    muggle_currency_code=muggle_currency_code)


async def get_muggle_money_value(ledger:VaultLedger, muggle_currency_code:str):

    with tracer.start_as_current_span("Calculating muggle value of vault"):
        # Goblins can be thorough...
        exchange : Dict[str,Dict]= {}
        for currency in MuggleCurrencies:
            exchange[currency.name] = await get_muggle_exchange_rates(currency.name)

        muggle_money_value = ledger.galleons * exchange[muggle_currency_code]["galleons"] + \
                             ledger.sickles * exchange[muggle_currency_code]["sickles"] + \
                             ledger.knuts * exchange[muggle_currency_code]["knuts"]
        return muggle_money_value
