import asyncio
import csv
import os
import random
import string
from typing import Dict, List

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from gringotts import config
from gringotts.models.vault import Vault
from gringotts.models.vault_key import VaultKey
from gringotts.models.vault_owner import VaultOwner
from gringotts.models.vault_ledger import VaultLedger



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


def generate_vaults(number: int, keys: List[VaultKey], max_vault_number) -> Dict[int,Vault]:
    # printing letters
    vaults = {}
    if len(keys) < number:
        raise Exception("must have more keys than vaults")

    for i in range(number):
        vault_number = i + max_vault_number
        vaults[vault_number]=Vault(vault_number=vault_number, vault_key_id=keys[i].key)
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

def add_special_vaults(vaults: Dict[str, Vault]):
    potter_vault = Vault(vault_number=713, vault_key_id="griffindoor")
    vaults[713]=potter_vault


async def seed(sm: sessionmaker = None):
    if not sm:
        sm = await create_session_maker()

    if await already_seeded(sm):
        return
        
    keys = generate_keys(100)
    potter_key = VaultKey('griffindoor')
    keys.append(potter_key)
    await save_all(sm, keys)

    current_max_vault = await get_max_vault_number(sm)
    vaults = generate_vaults(100, keys, current_max_vault + 1) 
      
    add_special_vaults(vaults)
    await save_all(sm, vaults.values())


    owners = import_wizards(vaults=vaults)
    await save_all(sm, owners)

async def already_seeded(async_session):
    async with async_session() as session:
        session: AsyncSession
        # make bulk insert
        harry = await VaultOwner.find(session,'hpotter')
        if harry:
            return True
        return False


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
                if name == 'Harry James Potter':
                    username='hpotter'
                    owners.append(VaultOwner(name=name,
                        species=species,
                        username='hpotter',
                        vault_id=713))

                else:
                    username = ''.join(ch for ch in name if ch.isalnum()).strip().lower()
                    owners.append(VaultOwner(name=name,
                                            species=species,
                                            username=username,
                                            vault_id=vaults[i].vault_number))
                i += 1
    return owners


if __name__ == '__main__':
    asyncio.run(seed())
