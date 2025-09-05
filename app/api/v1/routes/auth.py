from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from passlib.hash import bcrypt
from app.models.user import User, UserRole
from app.models.blacklisted_token import BlacklistedToken
from app.services.auth.jwt_handler import create_access_token, decode_access_token, create_refresh_token,decode_refresh_token
from app.schemas.auth_schema import PhoneCheckRequest, AuthCheckResponse, PasswordLoginRequest, SignupRequest, TokenResponse, RefreshRequest, LogoutResponse


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



    
# Check if user exists by phone number
@router.post("/check", response_model=AuthCheckResponse)
def check_user_exists(request: PhoneCheckRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if user:
        return AuthCheckResponse(user_exists=True, message="User exists. Please provide password to login.")
    else:
        return AuthCheckResponse(user_exists=False, message="User does not exist. Please provide name, password, and optional email to signup.")

# Login with password for existing user
@router.post("/login", response_model=TokenResponse)
def login(request: PasswordLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == request.phone_number).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please check user existence first.")

    if not bcrypt.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Handle None email properly
    access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "phone_number": user.phone_number
    })
    refresh_token = create_refresh_token({
        "user_id": user.id
    })
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

# Signup for new user
@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if phone number already exists
    existing_phone = db.query(User).filter(User.phone_number == request.phone_number).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Check if email is provided and already exists
    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = bcrypt.hash(request.password)
    new_user = User(
        name=request.name,
        phone_number=request.phone_number,
        email=request.email if request.email else None,
        password_hash=hashed_password,
        role=UserRole.user  # Default role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate tokens - handle None email properly
    access_token = create_access_token({
        "user_id": new_user.id,
        "email": new_user.email,
        "phone_number": new_user.phone_number
    })
    refresh_token = create_refresh_token({
        "user_id": new_user.id
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

