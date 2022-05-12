from typing import Optional

from pydantic import BaseModel


class AuthenticationRequest(BaseModel):
    vault_owner: str 
    vault_number: int
    vault_key: str


class AuthenticationResponse(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    vault_owner: Optional[str] = None



