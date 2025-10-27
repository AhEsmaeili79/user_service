import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.rabbitmq.producer import get_rabbitmq_producer
from app.rabbitmq.config import rabbitmq_config

logger = logging.getLogger(__name__)


class UserLookupService:
    """Service to handle user lookup requests from split service"""
    
    def __init__(self):
        self.producer = get_rabbitmq_producer()
    
    def lookup_user_by_phone_or_email(self, phone_or_email: str) -> Optional[Dict[str, Any]]:
        """
        Look up user by phone number or email
        
        Args:
            phone_or_email: Phone number or email to search for
            
        Returns:
            Dict containing user data if found, None otherwise
        """
        try:
            db = SessionLocal()
            try:
                # Try to find user by phone number first
                user = db.query(User).filter(User.phone_number == phone_or_email).first()
                
                # If not found by phone, try email
                if not user:
                    user = db.query(User).filter(User.email == phone_or_email).first()
                
                if user:
                    logger.info(f"✅ DATABASE LOOKUP SUCCESS: Found user {user.id} for {phone_or_email}")
                    logger.info(f"   📛 Name: {user.name}")
                    logger.info(f"   📞 Phone: {user.phone_number}")
                    logger.info(f"   📧 Email: {user.email}")
                    logger.info(f"   🔑 Role: {user.role.value}")
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
                else:
                    logger.info(f"❌ DATABASE LOOKUP FAILED: No user found for {phone_or_email}")
                    return None
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error looking up user {phone_or_email}: {e}")
            return None
    
    def publish_user_lookup_response(self, request_id: str, success: bool, user_data: Optional[Dict[str, Any]] = None, error_message: Optional[str] = None) -> bool:
        """
        Publish user lookup response to RabbitMQ
        
        Args:
            request_id: Original request ID to match response
            success: Whether the lookup was successful
            user_data: User data if found
            error_message: Error message if lookup failed
            
        Returns:
            bool: True if message published successfully, False otherwise
        """
        try:
            # Prepare response message
            response_data = {
                "request_id": request_id,
                "success": success,
                "timestamp": self._get_current_timestamp()
            }
            
            if success and user_data:
                response_data["user_data"] = user_data
            elif not success and error_message:
                response_data["error_message"] = error_message
            
            # Publish response
            success_published = self.producer.publish_message(
                exchange=rabbitmq_config.user_lookup_exchange,
                routing_key=rabbitmq_config.user_lookup_response_key,
                message=response_data,
                correlation_id=request_id
            )
            
            if success_published:
                if success and user_data:
                    logger.info(f"📤 RABBITMQ PUBLISH SUCCESS: Success response published for request {request_id}")
                    logger.info(f"   👤 User ID: {user_data.get('user_id')}")
                    logger.info(f"   📛 Name: {user_data.get('name')}")
                elif not success and error_message:
                    logger.info(f"📤 RABBITMQ PUBLISH SUCCESS: Error response published for request {request_id}")
                    logger.info(f"   ❌ Error: {error_message}")
            else:
                logger.error(f"❌ RABBITMQ PUBLISH FAILED: Could not publish response for request {request_id}")
            
            return success_published
            
        except Exception as e:
            logger.error(f"Error publishing user lookup response for {request_id}: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Global service instance
_user_lookup_service: Optional[UserLookupService] = None


def get_user_lookup_service() -> UserLookupService:
    """Get or create user lookup service instance"""
    global _user_lookup_service
    if _user_lookup_service is None:
        _user_lookup_service = UserLookupService()
    return _user_lookup_service
