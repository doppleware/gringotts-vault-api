import enum
from typing import List

from opentelemetry import trace
from sqlalchemy import Column, Enum, String, select, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from gringotts.models.base import Base
from gringotts.models.vault import Vault

tracer = trace.get_tracer(__name__)


class VaultOwner(Base):
    __tablename__ = "vault_owners"
    __table_args__ = {"schema": "gringotts"}



    class Species(enum.Enum):
        Human = 1
        Goblin = 2
        Centaur = 3
        Giant = 4
        Half_Human_Half_Giant = 5
        Werewolf = 6
        Unknown = 7

    username = Column(String, nullable=False, primary_key=True, unique=True)
    name = Column(String, nullable=False, primary_key=False, unique=True)
    species = Column(Enum(Species), nullable=False, primary_key=True, unique=False)

    vault_id :int = Column(Integer, ForeignKey('gringotts.vaults.vault_number'))
    vault :Vault = relationship("Vault", back_populates="owner")

    def __init__(self, name: str, username: str, species: Species, vault_id: int):
        self.name = name
        self.username = username
        self.species = species
        self.vault_id=vault_id

    @classmethod
    async def find(cls, db_session: AsyncSession, username: str):
        """

        :param db_session:
        :param name:
        :return:
        """
        with tracer.start_as_current_span("Retrieving vault owner by username"):
            stmt = select(cls).where(cls.username == username)
            result = await db_session.execute(stmt)
            instance = result.scalars().first()
            return instance
