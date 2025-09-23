from pydantic import BaseModel, validator
from typing import Optional, Union

class IdentifierRequest(BaseModel):
    identifier: str  # Can be either email or phone_number

    @validator('identifier')
    def validate_identifier(cls, v):
        if not v or not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()

class AuthCheckResponse(BaseModel):
    user_exists: bool
    message: str
    identifier_type: Optional[str] = None  # "email" or "phone_number"


class SignupRequest(BaseModel):
    identifier: str  # Can be either email or phone_number
    name: str

    class Config:
        extra = "forbid"  # Prevent extra fields

    @validator('identifier')
    def validate_identifier(cls, v):
        if not v or not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    msg: str
