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
        
class UserUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    card_number: str | None = None
    card_holder_name: str | None = None


        
