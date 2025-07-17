import uuid
from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from app.db.database import Base

class OtpCode(Base):
    __tablename__ = "otp_codes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_id = Column(String,ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    code = Column(String(5), nullable=False)  
    expires_at = Column(DateTime(timezone=True),nullable=False,index=True)
    is_used = Column(Boolean,nullable=False,default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)