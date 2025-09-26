from typing import Optional
from app.redis.cache import cache_set, cache_get, cache_delete, cache_exists


class TokenBlacklist:
    """Redis-based token blacklist service"""

    @staticmethod
    def blacklist_token(token: str, expires_in: int = 3600) -> bool:
        """
        Add a token to the blacklist

        Args:
            token: JWT token to blacklist
            expires_in: Time in seconds until token expires (default: 1 hour)

        Returns:
            True if successfully blacklisted, False otherwise
        """
        key = f"blacklist:{token}"
        return cache_set(key, "blacklisted", expire=expires_in)

    @staticmethod
    def is_blacklisted(token: str) -> bool:
        """
        Check if a token is blacklisted

        Args:
            token: JWT token to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        key = f"blacklist:{token}"
        return cache_exists(key)

    @staticmethod
    def remove_from_blacklist(token: str) -> bool:
        """
        Remove a token from the blacklist (useful for testing)

        Args:
            token: JWT token to remove

        Returns:
            True if successfully removed, False otherwise
        """
        key = f"blacklist:{token}"
        return cache_delete(key)

    @staticmethod
    def get_blacklist_status(token: str) -> Optional[str]:
        """
        Get the blacklist status of a token

        Args:
            token: JWT token to check

        Returns:
            "blacklisted" if token is blacklisted, None otherwise
        """
        key = f"blacklist:{token}"
        return cache_get(key)


# Convenience functions for direct use
def blacklist_token(token: str, expires_in: int = 3600) -> bool:
    """Add token to blacklist"""
    return TokenBlacklist.blacklist_token(token, expires_in)


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return TokenBlacklist.is_blacklisted(token)


def remove_token_from_blacklist(token: str) -> bool:
    """Remove token from blacklist"""
    return TokenBlacklist.remove_from_blacklist(token)