import json
import logging
from typing import Any, Optional, Union
import redis
from .connection import get_redis_client

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis-based caching service"""

    def __init__(self):
        self.client = get_redis_client()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.client:
                return None

            value = self.client.get(key)
            if value is None:
                return None

            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"Error getting cache key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration (in seconds)"""
        try:
            if not self.client:
                return False

            # Serialize value to JSON if it's not a string
            if not isinstance(value, str):
                try:
                    value = json.dumps(value)
                except (TypeError, ValueError) as e:
                    logger.error(f"Error serializing value for key '{key}': {e}")
                    return False

            result = self.client.set(key, value, ex=expire)
            return result is True

        except Exception as e:
            logger.error(f"Error setting cache key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if not self.client:
                return False

            result = self.client.delete(key)
            return result > 0

        except Exception as e:
            logger.error(f"Error deleting cache key '{key}': {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if not self.client:
                return False

            return self.client.exists(key) > 0

        except Exception as e:
            logger.error(f"Error checking cache key '{key}': {e}")
            return False

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key (in seconds)"""
        try:
            if not self.client:
                return False

            result = self.client.expire(key, seconds)
            return result is True

        except Exception as e:
            logger.error(f"Error setting expiration for cache key '{key}': {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get time to live for key in seconds (-2 if key doesn't exist, -1 if no expiration)"""
        try:
            if not self.client:
                return -2

            return self.client.ttl(key)

        except Exception as e:
            logger.error(f"Error getting TTL for cache key '{key}': {e}")
            return -2

    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment the number stored at key by amount"""
        try:
            if not self.client:
                return None

            return self.client.incr(key, amount)

        except Exception as e:
            logger.error(f"Error incrementing cache key '{key}': {e}")
            return None

    def flush_all(self) -> bool:
        """Clear all cache data (use with caution!)"""
        try:
            if not self.client:
                return False

            result = self.client.flushall()
            return result is True

        except Exception as e:
            logger.error(f"Error flushing cache: {e}")
            return False


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


# Convenience functions for direct use
def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    return get_cache().get(key)


def cache_set(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """Set value in cache"""
    return get_cache().set(key, value, expire)


def cache_delete(key: str) -> bool:
    """Delete key from cache"""
    return get_cache().delete(key)


def cache_exists(key: str) -> bool:
    """Check if key exists"""
    return get_cache().exists(key)
