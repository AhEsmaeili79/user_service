import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.redis.cache import get_cache
from app.rabbitmq.producer import get_rabbitmq_producer
from app.utils.validators import normalize_phone_number
from typing import Optional


class OTPHandler:
    """Handles OTP generation, validation, and messaging"""

    @staticmethod
    def generate_otp_code(length: int = 5) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def create_otp(user_id: str, db: Session = None) -> dict:
        """Create a new OTP for a user and store in Redis cache"""
        # Generate OTP code
        otp_code = OTPHandler.generate_otp_code()

        # Create cache key for the OTP
        cache_key = f"otp:{user_id}"

        # Prepare OTP data
        otp_data = {
            "code": otp_code,
            "created_at": datetime.utcnow().isoformat(),
            "is_used": False
        }

        # Store in Redis cache with 10-minute expiration
        cache = get_cache()
        success = cache.set(cache_key, otp_data, expire=600)  # 600 seconds = 10 minutes

        if not success:
            raise Exception("Failed to store OTP in cache")

        # Return OTP data (without exposing the actual code for security)
        return {
            "user_id": user_id,
            "code": otp_code,  # Only return for internal use (like sending)
            "expires_in": 600
        }

    @staticmethod
    def validate_otp(user_id: str, otp_code: str, db: Session = None) -> bool:
        """Validate an OTP code for a user from Redis cache"""
        cache_key = f"otp:{user_id}"
        cache = get_cache()

        # Get OTP data from cache
        otp_data = cache.get(cache_key)

        if not otp_data:
            return False

        # Check if OTP is already used
        if otp_data.get("is_used", False):
            return False

        # Check if the provided code matches
        if otp_data.get("code") != otp_code:
            return False

        # Check if OTP has expired (10 minutes from creation)
        created_at_str = otp_data.get("created_at")
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str)
                if datetime.utcnow() - created_at > timedelta(minutes=10):
                    # OTP expired, remove from cache
                    cache.delete(cache_key)
                    return False
            except (ValueError, TypeError):
                # Invalid date format, consider OTP invalid
                cache.delete(cache_key)
                return False

        # OTP is valid, remove it from cache immediately after validation
        cache.delete(cache_key)

        return True

    @staticmethod
    def get_user_by_identifier(identifier: str, db: Session) -> Optional[User]:
        """Get user by email or phone number"""
        # Check if it's an email or phone
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_email = re.match(email_pattern, identifier) is not None

        if is_email:
            return db.query(User).filter(User.email == identifier).first()
        else:
            # Normalize phone number before querying
            # Check both normalized and original to handle existing data with '+'
            normalized_phone = normalize_phone_number(identifier)
            return db.query(User).filter(
                or_(
                    User.phone_number == normalized_phone,
                    User.phone_number == identifier
                )
            ).first()

    @staticmethod
    def get_identifier_type(identifier: str) -> str:
        """Determine if identifier is email or phone_number"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return "email" if re.match(email_pattern, identifier) else "phone_number"

    @staticmethod
    def send_otp_message(identifier: str, otp_code: str, identifier_type: str) -> bool:
        """Send OTP message to RabbitMQ"""
        try:
            from app.rabbitmq.config import rabbitmq_config
            producer = get_rabbitmq_producer()

            # Determine routing key based on identifier type
            if identifier_type == "email":
                routing_key = rabbitmq_config.email_routing_key
            elif identifier_type == "phone_number":
                routing_key = rabbitmq_config.sms_routing_key
            else:
                print(f"Invalid identifier type: {identifier_type}")
                return False

            return producer.publish_otp_message(identifier, otp_code, routing_key)
        except Exception as e:
            print(f"Failed to send OTP message: {e}")
            return False