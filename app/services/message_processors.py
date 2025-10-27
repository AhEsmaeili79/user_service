"""
Ultra-clean message processing with advanced design patterns
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MessageContext:
    """Immutable message context"""
    request_id: str
    phone_or_email: str
    group_slug: str
    timestamp: str


class MessageHandler(ABC):
    """Abstract message handler"""
    
    @abstractmethod
    def handle(self, context: MessageContext) -> Dict[str, Any]:
        """Handle message and return response"""
        pass


class UserLookupHandler(MessageHandler):
    """Handles user lookup messages"""
    
    def __init__(self, user_service: Callable, publisher: Callable):
        self.user_service = user_service
        self.publisher = publisher
    
    def handle(self, context: MessageContext) -> Dict[str, Any]:
        """Handle user lookup"""
        user_data = self.user_service(context.phone_or_email)
        
        return {
            "request_id": context.request_id,
            "success": bool(user_data),
            "user_data": user_data,
            "error_message": None if user_data else f"User not found: {context.phone_or_email}",
            "timestamp": self._now()
        }
    
    @staticmethod
    def _now() -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()


class HandlerRegistry:
    """Registry for message handlers"""
    
    def __init__(self):
        self._handlers = {}
    
    def register(self, message_type: str, handler: MessageHandler):
        """Register handler for message type"""
        self._handlers[message_type] = handler
    
    def get_handler(self, message_type: str) -> Optional[MessageHandler]:
        """Get handler for message type"""
        return self._handlers.get(message_type)


def log_execution(func):
    """Decorator for logging function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"🔄 Executing {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"✅ {func.__name__} completed")
        return result
    return wrapper