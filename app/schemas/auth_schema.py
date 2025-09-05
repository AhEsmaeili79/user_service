from pydantic import BaseModel
from typing import Optional

class PhoneCheckRequest(BaseModel):
    phone_number: str

class AuthCheckResponse(BaseModel):
    user_exists: bool
    message: str

class PasswordLoginRequest(BaseModel):
    phone_number: str
    password: str

class SignupRequest(BaseModel):
    phone_number: str
    name: str
    password: str
    email: Optional[str] = None

    class Config:
        extra = "forbid"  # Prevent extra fields

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    msg: str
