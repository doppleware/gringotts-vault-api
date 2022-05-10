
from pydantic import BaseModel, Field


class VaultBalanceResponse(BaseModel):
    vault_number: int 
    galleons: int
    sickle: int
    knut: int

