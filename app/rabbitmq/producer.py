import json
import logging
from typing import Dict, Any, Optional
import pika
from .config import rabbitmq_config
from .setup import RabbitMQSetup

logger = logging.getLogger(__name__)


class RabbitMQProducer:
    """Handles publishing messages to RabbitMQ"""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.setup = RabbitMQSetup()
    
    def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        try:
            self.connection = self.setup.create_connection()
            self.channel = self.connection.channel()
            logger.info("RabbitMQ producer connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect RabbitMQ producer: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close RabbitMQ connection"""
        if self.channel and not self.channel.is_closed:
            self.channel.close()
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        logger.info("RabbitMQ producer disconnected")
    
    def publish_otp_message(self, identifier: str, otp_code: str, identifier_type: str) -> bool:
        """
        Publish OTP message to appropriate queue based on identifier type
        
        Args:
            identifier: Email or phone number
            otp_code: The OTP code to send
            identifier_type: "email" or "phone"
        
        Returns:
            bool: True if message published successfully, False otherwise
        """
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        try:
            # Prepare message data
            message_data = {
                "identifier": identifier,
                "otp_code": otp_code,
                "identifier_type": identifier_type,
                "timestamp": None  # Will be set by the consumer
            }
            
            # Determine routing key and queue
            if identifier_type == "email":
                routing_key = rabbitmq_config.email_routing_key
            elif identifier_type == "phone":
                routing_key = rabbitmq_config.sms_routing_key
            else:
                logger.error(f"Invalid identifier type: {identifier_type}")
                return False
            
            # Publish message
            self.channel.basic_publish(
                exchange=rabbitmq_config.otp_exchange,
                routing_key=routing_key,
                body=json.dumps(message_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published OTP message for {identifier_type}: {identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish OTP message: {e}")
            return False
    
    def publish_email_otp(self, email: str, otp_code: str) -> bool:
        """Convenience method for publishing email OTP"""
        return self.publish_otp_message(email, otp_code, "email")
    
    def publish_sms_otp(self, phone_number: str, otp_code: str) -> bool:
        """Convenience method for publishing SMS OTP"""
        return self.publish_otp_message(phone_number, otp_code, "phone")


# Global producer instance
_rabbitmq_producer: Optional[RabbitMQProducer] = None


def get_rabbitmq_producer() -> RabbitMQProducer:
    """Get or create RabbitMQ producer instance"""
    global _rabbitmq_producer
    if _rabbitmq_producer is None:
        _rabbitmq_producer = RabbitMQProducer()
        _rabbitmq_producer.connect()
    return _rabbitmq_producer


def close_rabbitmq_producer() -> None:
    """Close RabbitMQ producer connection"""
    global _rabbitmq_producer
    if _rabbitmq_producer:
        _rabbitmq_producer.disconnect()
        _rabbitmq_producer = None
