import logging
from typing import Optional
import redis
from ..core.config import redis_config

logger = logging.getLogger(__name__)


class RedisConnection:
    """Manages Redis connection lifecycle"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    def connect(self) -> bool:
        """Establish connection to Redis"""
        try:
            self.client = redis.Redis(
                host=redis_config.host,
                port=redis_config.port,
                password=redis_config.password,
                db=redis_config.db,
                max_connections=redis_config.max_connections,
                socket_timeout=redis_config.socket_timeout,
                socket_connect_timeout=redis_config.socket_connect_timeout,
                decode_responses=True
            )

            # Test the connection
            self.client.ping()

            logger.info(f"Connected to Redis at {redis_config.host}:{redis_config.port}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False

    def is_connected(self) -> bool:
        """Check if connection is active"""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def disconnect(self) -> None:
        """Close Redis connection"""
        try:
            if self.client:
                self.client.close()
                self.client = None
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    def get_client(self) -> Optional[redis.Redis]:
        """Get the Redis client for operations"""
        if not self.is_connected():
            if not self.connect():
                return None
        return self.client


def check_redis_health() -> bool:
    """Check if Redis is accessible and healthy"""
    connection = RedisConnection()
    try:
        if connection.connect():
            logger.info("Redis health check passed")
            return True
        else:
            logger.error("Redis health check failed")
            return False
    finally:
        connection.disconnect()


# Global connection instance
_redis_connection: Optional[RedisConnection] = None


def get_redis_connection() -> RedisConnection:
    """Get or create Redis connection instance"""
    global _redis_connection
    if _redis_connection is None or not _redis_connection.is_connected():
        _redis_connection = RedisConnection()
        _redis_connection.connect()
    return _redis_connection


def close_redis_connection() -> None:
    """Close Redis connection"""
    global _redis_connection
    if _redis_connection:
        _redis_connection.disconnect()
        _redis_connection = None


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client directly"""
    connection = get_redis_connection()
    return connection.get_client()
