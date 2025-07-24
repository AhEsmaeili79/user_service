from pydantic import BaseModel

class LoginRequest(BaseModel):
    identifier: str
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    
class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    msg: str
