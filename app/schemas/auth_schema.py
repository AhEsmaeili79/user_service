from pydantic import BaseModel, field_validator
from typing import Optional

class IdentifierRequest(BaseModel):
    identifier: str  # Can be either email or phone_number

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()

class AuthCheckResponse(BaseModel):
    user_exists: bool
    message: str
    identifier_type: Optional[str] = None  # "email" or "phone_number"


class RequestOTPRequest(BaseModel):
    identifier: str  # Can be either email or phone_number

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()


class VerifyOTPRequest(BaseModel):
    identifier: str  # Can be either email or phone_number
    otp_code: str

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()

    @field_validator('otp_code')
    @classmethod
    def validate_otp_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('OTP code cannot be empty')
        if len(v.strip()) != 5:
            raise ValueError('OTP code must be 5 digits')
        if not v.strip().isdigit():
            raise ValueError('OTP code must contain only digits')
        return v.strip()


class RequestOTPResponse(BaseModel):
    message: str
    identifier_type: str


class VerifyOTPResponse(BaseModel):
    access_token: str
    refresh_token: str
    is_new_user: bool  # True if user was created, False if existing user

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    msg: str
