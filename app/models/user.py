import enum
import uuid
from sqlalchemy.sql import func
import uuid
from sqlalchemy import Column, String, DateTime, Enum
from db.database import Base

from sqlalchemy.orm import Mapped, mapped_column


class UserRole(str, enum.Enum):
    user = "user"
    group_admin = "group_admin"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)  # Specify a maximum length for name
    phone_number = Column(String(15), unique=True, nullable=False, index=True)  # Limit phone number length
    password_hash = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    card_number = Column(String, nullable=True)
    card_holder_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)  # Set default role
    email = Column(String(255), unique=True, nullable=False, index=True)  # Limit email length
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

