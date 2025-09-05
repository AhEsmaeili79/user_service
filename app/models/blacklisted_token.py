import uuid 
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.db.database import Base
from sqlalchemy.sql import func

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    token = Column(String, nullable=False, index=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)