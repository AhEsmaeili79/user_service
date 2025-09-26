import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp_code import OtpCode
from app.models.user import User
from app.rabbitmq.producer import get_rabbitmq_producer
from typing import Optional


class OTPHandler:
    """Handles OTP generation, validation, and messaging"""

    @staticmethod
    def generate_otp_code(length: int = 5) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def create_otp(user_id: str, db: Session) -> OtpCode:
        """Create a new OTP for a user"""
        # Generate OTP code
        otp_code = OTPHandler.generate_otp_code()

        # Set expiration (5 minutes from now)
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Create OTP record
        otp = OtpCode(
            user_id=user_id,
            code=otp_code,
            expires_at=expires_at,
            is_used=False
        )

        db.add(otp)
        db.commit()
        db.refresh(otp)

        return otp

    @staticmethod
    def validate_otp(user_id: str, otp_code: str, db: Session) -> bool:
        """Validate an OTP code for a user"""
        # Find the most recent unused OTP for this user
        otp = db.query(OtpCode).filter(
            OtpCode.user_id == user_id,
            OtpCode.code == otp_code,
            OtpCode.is_used == False,
            OtpCode.expires_at > datetime.utcnow()
        ).order_by(OtpCode.created_at.desc()).first()

        if not otp:
            return False

        # Mark OTP as used
        otp.is_used = True
        db.commit()

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
            return db.query(User).filter(User.phone_number == identifier).first()

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