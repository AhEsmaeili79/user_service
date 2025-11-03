import re
from fastapi import HTTPException

def normalize_phone_number(phone: str) -> str:
    """Normalize phone number by removing leading '+' if present"""
    if not phone:
        return phone
    return phone.lstrip('+')

def validate_name(value):
    if not re.match(r"^[A-Za-z\s]{2,100}$", value):
        raise HTTPException(status_code=400, detail="Invalid name format")

def validate_phone_number(value):
    if not re.match(r"^\+?\d{10,15}$", value):
        raise HTTPException(status_code=400, detail="Invalid phone number format")

def validate_email(value):
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
        raise HTTPException(status_code=400, detail="Invalid email format")

def validate_card_number(value):
    if value and not re.match(r"^\d{16}$", value):
        raise HTTPException(status_code=400, detail="Invalid card number format")

def validate_card_holder_name(value):
    if value and not re.match(r"^[A-Za-z\s]{2,100}$", value):
        raise HTTPException(status_code=400, detail="Invalid card holder name format")

def validate_avatar_url(value):
    if value and not re.match(r"^https?://.+$", value):
        raise HTTPException(status_code=400, detail="Invalid avatar URL format")

def validate_role(value):
    if value not in ["user", "group_admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

FIELD_VALIDATORS = {
    "name": validate_name,
    "phone_number": validate_phone_number,
    "email": validate_email,
    "card_number": validate_card_number,
    "card_holder_name": validate_card_holder_name,
    "avatar_url": validate_avatar_url,
    "role": validate_role,
} 