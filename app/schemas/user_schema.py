from pydantic import BaseModel, EmailStr
from typing import Optional
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