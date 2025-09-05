from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate , UserOut, UserUpdate
from passlib.hash import bcrypt
from app.db.database import get_db
from app.services.auth.jwt_handler import decode_access_token
from app.models.blacklisted_token import BlacklistedToken
from app.services.user_service import validate_and_update_user

router = APIRouter(prefix='/users',tags=["users"])
        
# User creation is now handled through /auth/signup endpoint

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
