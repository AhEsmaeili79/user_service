from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schema import UserCreate , UserOut, UserUpdate
from passlib.hash import bcrypt
from db.database import get_db
from services.auth.jwt_handler import decode_access_token
from models.blacklisted_token import BlacklistedToken
from services.user_service import validate_and_update_user

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

# Get current user info
@router.get("/profile", response_model=UserOut)
def get_current_user_info(
    access_token: str = Header(..., description="Access token (without Bearer)"),
    db: Session = Depends(get_db)
):
    if access_token.startswith("Bearer "):
        access_token = access_token.replace("Bearer ", "")
    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter_by(id=payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user profile
@router.patch("/profile", response_model=UserOut)
def update_user_profile(
    update: UserUpdate,
    access_token: str = Header(..., description="Access token (without Bearer)"),
    db: Session = Depends(get_db)
):
    token = access_token.removeprefix("Bearer ").strip()
    if db.query(BlacklistedToken).filter_by(token=token).first():
        raise HTTPException(status_code=401, detail="Token blacklisted")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter_by(id=payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = validate_and_update_user(user, update, db)
    db.commit()
    db.refresh(user)
    return user
