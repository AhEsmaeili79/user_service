import uuid
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import UUID
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
    
class OtpCode(Base):
    __tablename__ = "otp_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    ode = Column(String(5), nullable=False)  
    expires_at = Column(DateTime(timezone=True),nullable=False,index=True)
    is_used = Column(Boolean,nullable=False,default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) 