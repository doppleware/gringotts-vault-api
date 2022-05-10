import asyncio
import csv
import os
import random
import string
from typing import List

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, query, Query

from gringotts import config
from gringotts.models.vault import Vault
from gringotts.models.vault_key import VaultKey
from gringotts.models.vault_owner import VaultOwner


def clean_string(value: str):
    return value.replace('-', '_').replace('/', '_').replace('\\', '_')


def convert_to_enum(value: str):
    try:
        return VaultOwner.Species[clean_string(value)]
    except:
        return VaultOwner.Species.Unknown


async def save_all(async_session: sessionmaker,
                   entities: List):
    async with async_session() as session:
        session: AsyncSession
        # make bulk insert
        session.add_all(entities)
        await session.commit()


def generate_keys(number: int) -> List[VaultKey]:
    # printing letters
    keys = []
    for i in range(number):
        keys.append(VaultKey(generate_key()))
    return keys


def generate_vaults(number: int, keys: List[VaultKey], max_vault_number) -> List[Vault]:
    # printing letters
    vaults = []
    if len(keys) < number:
        raise Exception("must have more keys than vaults")

    for i in range(number):
        vaults.append(Vault(vault_number=i + max_vault_number, vault_key_id=keys[i].key))
    return vaults


def generate_key():
    letters = string.ascii_letters
    return (''.join(random.choice(letters) for i in range(10)))


async def get_max_vault_number(async_session: sessionmaker):
    async with async_session() as session:
        session: AsyncSession
        result = await session.execute(
            sqlalchemy.select([Vault.vault_number]).order_by(Vault.vault_number.desc()).limit(1))
        number = result.scalars().first()
        if not number:
            return 0
        return number


async def seed(sm: sessionmaker = None):
    if not sm:
        sm = await create_session_maker()

    keys = generate_keys(10000)
    await save_all(sm, keys)

    current_max_vault = await get_max_vault_number(sm)
    vaults = generate_vaults(1000, keys, current_max_vault + 1)
    await save_all(sm, vaults)

    owners = import_wizards(vaults=vaults)
    await save_all(sm, owners)


async def create_session_maker():
    global_settings = config.get_settings()
    url = global_settings.asyncpg_url
    engine = create_async_engine(
        url,
        future=True,
        echo=True,
    )
    s = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return s


def import_wizards(vaults: List[Vault]):
    owners = []
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    # get fixture data from JSONPlaceholder
    with open(os.path.join(__location__, 'vault_owners.csv'), newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        headerRow = True

        species_index = 0
        name_index = 0
        i = 0
        for row in spamreader:
            if i >= len(vaults):
                break

            if headerRow:
                species_index = row.index('Species')
                name_index = row.index('Name')
                headerRow = False
            else:
                if (len(row) - 1 < species_index):
                    continue
                name: str = row[name_index]
                if not name:
                    continue
                species = convert_to_enum(row[species_index])
                username = ''.join(ch for ch in name if ch.isalnum()).strip().lower()
                owners.append(VaultOwner(name=name,
                                         species=species,
                                         username=username,
                                         vault_id=vaults[i].vault_number))
                i += 1
    return owners


if __name__ == '__main__':
    asyncio.run(seed())
