import sqlalchemy
from opentelemetry import trace
from sqlalchemy import Column, Integer, ForeignKey, DateTime, ForeignKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from gringotts.models.base import Base
from gringotts.models.vault import Vault

tracer = trace.get_tracer(__name__)


class VaultLedger(Base):
    __tablename__ = "vault_ledgers"
    __table_args__ = {"schema": "gringotts"}

    vault_number = Column(Integer, ForeignKey('gringotts.vaults.vault_number'), nullable=False, primary_key=True,
                          unique=True)
    vault: Vault = relationship("Vault", back_populates="ledger")
    last_appraised = Column(DateTime, nullable=True)
    sickles = Column(Integer, nullable=False, primary_key=False, unique=False, default=0)
    knuts = Column(Integer, nullable=False, primary_key=False, unique=False, default=0)
    galleons = Column(Integer, nullable=False, primary_key=False, unique=False, default=0)

    def __init__(self, vault_number):
        self.vault_number = vault_number

    @classmethod
    async def find_by_vault_id(cls, db_session: AsyncSession, number: int):
        """

        :param db_session:
        :param number:
        :return:
        """
        with tracer.start_as_current_span('Retrieving ledger by vault number'):
            stmt = sqlalchemy.select(cls).where(cls.vault_number == number)
            result = await db_session.execute(stmt)
            instance = result.scalars().first()
            return instance
