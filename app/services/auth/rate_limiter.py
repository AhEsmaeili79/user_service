import time
from typing import Optional
from app.redis.cache import get_cache, cache_get, cache_set, cache_incr

# Rate limiting configuration
MAX_REQUESTS_PER_MINUTE = 60
WINDOW_SECONDS = 60


class RateLimiter:
    """Redis-based rate limiter"""

    def __init__(self):
        self.cache = get_cache()

    def _get_key(self, identifier: str) -> str:
        """Generate cache key for rate limiting"""
        return f"rate_limit:{identifier}"

    def is_rate_limited(self, identifier: str) -> bool:
        """
        Check if the identifier is rate limited

        Args:
            identifier: Unique identifier (e.g., user ID, IP address)

        Returns:
            True if rate limited, False otherwise
        """
        key = self._get_key(identifier)
        current_time = int(time.time())

        # Get current request count
        request_count = cache_get(key) or 0

        # Reset counter if window has passed
        if request_count == 0:
            # First request in this window
            cache_set(key, 1, expire=WINDOW_SECONDS)
            return False

        if request_count >= MAX_REQUESTS_PER_MINUTE:
            return True

        # Increment counter
        new_count = cache_incr(key, 1)
        if new_count is None:
            # Fallback if increment fails
            return False

        return new_count > MAX_REQUESTS_PER_MINUTE

    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests allowed for the identifier"""
        key = self._get_key(identifier)
        current_count = cache_get(key) or 0
        remaining = max(0, MAX_REQUESTS_PER_MINUTE - current_count)
        return remaining

    def get_reset_time(self, identifier: str) -> Optional[int]:
        """Get the time when the rate limit resets (Unix timestamp)"""
        key = self._get_key(identifier)
        ttl = self.cache.ttl(key)

        if ttl == -2:  # Key doesn't exist
            return None
        elif ttl == -1:  # Key exists but no expiration
            return None
        else:
            return int(time.time()) + ttl


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Convenience functions
def check_rate_limit(identifier: str) -> bool:
    """Check if identifier is rate limited"""
    return get_rate_limiter().is_rate_limited(identifier)


def get_remaining_requests(identifier: str) -> int:
    """Get remaining requests for identifier"""
    return get_rate_limiter().get_remaining_requests(identifier)


def get_rate_limit_reset_time(identifier: str) -> Optional[int]:
    """Get rate limit reset time for identifier"""
    return get_rate_limiter().get_reset_time(identifier)