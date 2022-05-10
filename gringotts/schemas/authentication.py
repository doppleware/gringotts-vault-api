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
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

