from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session 
from sqlalchemy import or_
from db.database import get_db
from passlib.hash import bcrypt
from models.user import User
from models.blacklisted_token import BlacklistedToken
from services.auth.jwt_handler import create_access_token, decode_access_token, create_refresh_token,decode_refresh_token
from schemas.auth_schema import LoginRequest, TokenResponse, RefreshRequest, LogoutResponse


router = APIRouter(prefix="/auth",tags=["Auth"])
    
    
# check current user
@router.post("/check-user")
def check_user(
    access_token: str = Header(..., description="Access token (without Bearer)") ,
    db: Session = Depends(get_db)
):
    if access_token.startswith("Bearer "):
        access_token = access_token.replace("Bearer ", "")
    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Check if token is blacklisted
    if db.query(BlacklistedToken).filter_by(token=access_token).first():
        raise HTTPException(status_code=401, detail="Token blacklisted")
    return {"msg": "Token is valid"}



    
# login
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
    refresh_token = create_refresh_token({
        "user_id": user.id
    })
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# refresh token
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_refresh_token(request.refresh_token)
    if not payload: 
        raise HTTPException(status_code=401, detail="Invalid refresh token")


    if db.query(BlacklistedToken).filter_by(token=request.refresh_token).first():
        raise HTTPException(status_code=401, detail="Token Blacklisted")

    user_id = payload["user_id"]
    user = db.query(User).filter_by(id=user_id).first()
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    access_token = create_access_token({
    "user_id": user.id,
    "email": user.email,
    "phone_number": user.phone_number
    })
    refresh_token = create_refresh_token({"user_id": user.id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# logout
@router.post("/logout", response_model=LogoutResponse)
def logout(
    access_token: str = Header(..., description="Access token (without Bearer)"),
    db: Session = Depends(get_db)
):
    if access_token.startswith("Bearer "):
        access_token = access_token.replace("Bearer ", "")

    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    db.add(BlacklistedToken(user_id=payload["user_id"], token=access_token))
    db.commit()
    return {"msg": "Token blacklisted successfully"}

