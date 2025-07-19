from pydantic import BaseModel, EmailStr
from enum import Enum

class RoleEnum(str, Enum):
    user = "user"
    group_admin = "group_admin"
    
class UserCreate(BaseModel):
    name : str 
    phone_number : str
    email : EmailStr
    password : str
    role : RoleEnum

class UserOut(BaseModel):
    id : str
    name : str 
    phone_number : str
    email : EmailStr
    role : RoleEnum
     
    class Config:
        from_attributes = True
        
        
class LoginRequest(BaseModel):
    identifier: str
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    
class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    refresh_token: str
    msg: str

class LogoutRequest(BaseModel):
    refresh_token: str
    
