import logging
from .connection import check_redis_health

logger = logging.getLogger(__name__)


def init_redis() -> None:
    """Initialize Redis connection and verify connectivity"""
    logger.info("Starting Redis initialization...")
    try:
        if check_redis_health():
            logger.info("Redis setup completed successfully")
        else:
            logger.error("Redis health check failed")
            logger.warning("Application will continue without Redis caching functionality")
    except Exception as e:
        logger.error(f"Failed to setup Redis: {e}")
        logger.warning("Application will continue without Redis caching functionality")
