from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.blacklisted_token import BlacklistedToken
from app.services.auth.jwt_handler import create_access_token, decode_access_token, create_refresh_token,decode_refresh_token
from app.schemas.auth_schema import IdentifierRequest, AuthCheckResponse, SignupRequest, TokenResponse, RefreshRequest, LogoutResponse


router = APIRouter(prefix="/auth",tags=["Auth"])


def is_email(identifier: str) -> bool:
    """Check if identifier is an email address"""
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, identifier) is not None

def get_identifier_type(identifier: str) -> str:
    """Determine if identifier is email or phone_number"""
    return "email" if is_email(identifier) else "phone_number"


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



    
# Check if user exists by email or phone number
@router.post("/check", response_model=AuthCheckResponse)
def check_user_exists(request: IdentifierRequest, db: Session = Depends(get_db)):
    identifier_type = get_identifier_type(request.identifier)

    if identifier_type == "email":
        user = db.query(User).filter(User.email == request.identifier).first()
    else:
        user = db.query(User).filter(User.phone_number == request.identifier).first()

    if user:
        return AuthCheckResponse(
            user_exists=True,
            message="User exists. Please provide password to login.",
            identifier_type=identifier_type
        )
    else:
        return AuthCheckResponse(
            user_exists=False,
            message="User does not exist. Please provide name and password to signup.",
            identifier_type=identifier_type
        )


# Signup for new user
@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    identifier_type = get_identifier_type(request.identifier)

    # Check if identifier already exists
    if identifier_type == "email":
        existing_user = db.query(User).filter(
            or_(User.email == request.identifier, User.phone_number == request.identifier)
        ).first()
        if existing_user:
            if existing_user.email == request.identifier:
                raise HTTPException(status_code=400, detail="Email already registered")
            else:
                raise HTTPException(status_code=400, detail="Phone number already registered")
    else:  # phone_number
        existing_user = db.query(User).filter(
            or_(User.phone_number == request.identifier, User.email == request.identifier)
        ).first()
        if existing_user:
            if existing_user.phone_number == request.identifier:
                raise HTTPException(status_code=400, detail="Phone number already registered")
            else:
                raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    if identifier_type == "email":
        new_user = User(
            name=request.name,
            phone_number=None,
            email=request.identifier,
            role=UserRole.user  # Default role
        )
    else:  # phone_number
        new_user = User(
            name=request.name,
            phone_number=request.identifier,
            email=None,
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

