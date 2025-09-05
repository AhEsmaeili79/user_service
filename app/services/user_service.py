import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserUpdate
from app.utils.validators import FIELD_VALIDATORS

def validate_and_update_user(user: User, update: UserUpdate, db: Session):
    updates = update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if value is None or value == "" or getattr(user, field) == value:
            continue
        # Validate using strategy pattern
        validator = FIELD_VALIDATORS.get(field)
        if validator:
            validator(value)
        # Uniqueness checks
        if field == "phone_number":
            if db.query(User).filter(User.phone_number == value, User.id != user.id).first():
                raise HTTPException(status_code=400, detail="Phone number already registered")
        if field == "email":
            if db.query(User).filter(User.email == value, User.id != user.id).first():
                raise HTTPException(status_code=400, detail="Email already registered")
        setattr(user, field, value)
    return user 