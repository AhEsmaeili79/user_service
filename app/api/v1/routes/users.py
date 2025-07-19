from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schema import UserCreate , UserOut
from passlib.hash import bcrypt
from db.database import get_db

router = APIRouter(prefix='/users',tags=["users"])
        
@router.post("/",response_model=UserOut)
def create_user(user:UserCreate,db: Session = Depends(get_db)):
    db_user = db.query(User).filter((User.email == user.email) | (User.phone_number == user.phone_number)).first()
    if db_user :
        raise HTTPException(status_code=400, detail="Email or Phone Number already registred!")
    
    hashed_password = bcrypt.hash(user.password)
    new_user = User(
        name = user.name,
        phone_number = user.phone_number,
        email = user.email,
        password_hash = hashed_password,
        role = user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

