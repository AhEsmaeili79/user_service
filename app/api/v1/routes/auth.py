from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session 
from sqlalchemy import or_
from app.db.database import SessionLocal
from app.models.user import User
from app.models.blacklisted_token import BlacklistedToken
from app.services.auth.jwt_handler import create_access_token,decode_access_token
from passlib.hash import bcrypt
from typing import cast
from pydantic import BaseModel


router = APIRouter(prefix="/auth",tags=["Auth"])


class LoginRequest(BaseModel):
    identifier: str
    password: str
    
class TokenResponse(BaseModel):
    access_token: str

class LogoutResponse(BaseModel):
    msg: str
    
    
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()
        
        
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        or_(
            User.email == request.identifier,
            User.phone_number == request.identifier
            )
        ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({
        "user_id": user.id, 
        "email": user.email,
        "phone_number": user.phone_number
        })
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    authorization: str = Header(..., description="Authorization token with Bearer scheme", example="Bearer eyJ0eXAiOiJKV1QiLCJhbGci..."),
    db: Session = Depends(get_db)
):
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    blacklisted = BlacklistedToken(user_id = payload["user_id"], token = token )
    db.add(blacklisted)
    db.commit()
    return {"msg": "Token blacklisted successfully"}