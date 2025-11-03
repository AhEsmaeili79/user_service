"""
Ultra-clean user lookup service
"""
import logging
import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import SessionLocal
from app.models.user import User
from app.rabbitmq.producer import get_rabbitmq_producer
from app.rabbitmq.config import rabbitmq_config
from app.utils.validators import normalize_phone_number

logger = logging.getLogger(__name__)


class UserLookupService:
    """Ultra-clean user lookup service"""
    
    def __init__(self):
        self.producer = get_rabbitmq_producer()
    
    def __call__(self, phone_or_email: str) -> Optional[Dict[str, Any]]:
        """Make service callable for cleaner usage"""
        return self.lookup_user(phone_or_email)
    
    def lookup_user(self, phone_or_email: str) -> Optional[Dict[str, Any]]:
        """Look up user by phone or email"""
        try:
            with SessionLocal() as db:
                user = self._find_user(db, phone_or_email)
                return self._to_dict(user) if user else None
        except Exception as e:
            logger.error(f"Lookup failed for {phone_or_email}: {e}")
            return None
    
    def _find_user(self, db: Session, phone_or_email: str) -> Optional[User]:
        """Find user in database"""
        # Check if it's an email or phone
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_email = re.match(email_pattern, phone_or_email) is not None
        
        if is_email:
            return db.query(User).filter(User.email == phone_or_email).first()
        else:
            # Normalize phone number before querying
            # Check both normalized and original to handle existing data with '+'
            normalized_phone = normalize_phone_number(phone_or_email)
            return db.query(User).filter(
                or_(
                    User.phone_number == normalized_phone,
                    User.phone_number == phone_or_email
                )
            ).first()
    
    def _to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "user_id": user.id,
            "name": user.name,
            "phone_number": user.phone_number,
            "email": user.email,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
            "card_number": user.card_number,
            "card_holder_name": user.card_holder_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    
    def publish(self, data: Dict[str, Any]) -> bool:
        """Publish response"""
        try:
            return self.producer.publish_message(
                exchange=rabbitmq_config.user_lookup_exchange,
                routing_key=rabbitmq_config.user_lookup_response_key,
                message=data,
                correlation_id=data.get("request_id")
            )
        except Exception as e:
            logger.error(f"Publish failed: {e}")
            return False


# Singleton
_service = None

def get_service() -> UserLookupService:
    """Get singleton service"""
    global _service
    return _service or (_service := UserLookupService())