import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user_schema import UserUpdate
from app.utils.validators import FIELD_VALIDATORS, normalize_phone_number

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
            # Normalize phone number before checking uniqueness and storing
            normalized_phone = normalize_phone_number(value)
            # Check both normalized and original for uniqueness (handle existing data with '+')
            existing_user = db.query(User).filter(
                or_(
                    User.phone_number == normalized_phone,
                    User.phone_number == value
                ),
                User.id != user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Phone number already registered")
            setattr(user, field, normalized_phone)
        elif field == "email":
            if db.query(User).filter(User.email == value, User.id != user.id).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            setattr(user, field, value)
        else:
            setattr(user, field, value)
    return user 