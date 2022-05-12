from typing import Optional

from pydantic import BaseModel, Field


class VaultBalanceResponse(BaseModel):
    vault_number: int 
    galleons: int
    sickles: int
    knuts: int
    muggle_currency_value: float
    muggle_currency_code: Optional[str] = None

