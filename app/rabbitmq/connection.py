import logging
from typing import Optional
import pika
from .config import rabbitmq_config

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """Manages RabbitMQ connection lifecycle"""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
    
    def connect(self) -> bool:
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                rabbitmq_config.username, 
                rabbitmq_config.password
            )
            
            parameters = pika.ConnectionParameters(
                host=rabbitmq_config.host,
                port=rabbitmq_config.port,
                virtual_host=rabbitmq_config.virtual_host,
                credentials=credentials,
                heartbeat=rabbitmq_config.heartbeat,
                connection_attempts=rabbitmq_config.connection_attempts,
                retry_delay=rabbitmq_config.retry_delay
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"Connected to RabbitMQ at {rabbitmq_config.host}:{rabbitmq_config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return (
            self.connection is not None 
            and not self.connection.is_closed 
            and self.channel is not None 
            and not self.channel.is_closed
        )
    
    def disconnect(self) -> None:
        """Close RabbitMQ connection"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
    
    def get_channel(self) -> Optional[pika.channel.Channel]:
        """Get the channel for operations"""
        if not self.is_connected():
            if not self.connect():
                return None
        return self.channel


def check_rabbitmq_health() -> bool:
    """Check if RabbitMQ is accessible and healthy"""
    connection = RabbitMQConnection()
    try:
        if connection.connect():
            logger.info("RabbitMQ health check passed")
            return True
        else:
            logger.error("RabbitMQ health check failed")
            return False
    finally:
        connection.disconnect()


# Global connection instance
_rabbitmq_connection: Optional[RabbitMQConnection] = None


def get_rabbitmq_connection() -> RabbitMQConnection:
    """Get or create RabbitMQ connection instance"""
    global _rabbitmq_connection
    if _rabbitmq_connection is None or not _rabbitmq_connection.is_connected():
        _rabbitmq_connection = RabbitMQConnection()
        _rabbitmq_connection.connect()
    return _rabbitmq_connection


def close_rabbitmq_connection() -> None:
    """Close RabbitMQ connection"""
    global _rabbitmq_connection
    if _rabbitmq_connection:
        _rabbitmq_connection.disconnect()
        _rabbitmq_connection = None
