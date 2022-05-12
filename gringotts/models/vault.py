from opentelemetry import trace
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
import sqlalchemy.sql.expression
from gringotts.models.base import Base
from gringotts.models.vault_key import VaultKey

tracer = trace.get_tracer(__name__)


class Vault(Base):

    __tablename__ = "vaults"
    __table_args__ = {"schema": "gringotts"}

    vault_number = Column(Integer, nullable=False, primary_key=True, unique=True)

    owner = relationship("VaultOwner", back_populates="vault", lazy="joined", innerjoin=True, uselist=False)
    ledger = relationship("VaultLedger", back_populates="vault")

    vault_key_id = Column(String, ForeignKey('gringotts.vault_keys.key'))
    key : VaultKey= relationship("VaultKey", back_populates="vault")

    def __init__(self, vault_number: int, vault_key_id):
        self.vault_number = vault_number
        self.vault_key_id = vault_key_id

    @classmethod
    async def find(cls, db_session: AsyncSession, number: int):
        """

        :param db_session:
        :param number:
        :return:
        """
        with tracer.start_as_current_span('Retrieving vault by number'):
            stmt = sqlalchemy.select(cls).where(cls.vault_number == number)
            result = await db_session.execute(stmt)
            instance = result.scalars().first()
            return instance
