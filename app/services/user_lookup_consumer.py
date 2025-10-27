"""
Ultra-clean consumer manager
"""
import logging
import threading
from typing import Optional
from app.rabbitmq.consumer import get_rabbitmq_consumer, create_user_lookup_callback
from app.rabbitmq.config import rabbitmq_config
from app.services.user_lookup_service import get_service
from app.services.message_processors import MessageContext, UserLookupHandler, HandlerRegistry

logger = logging.getLogger(__name__)


class ConsumerManager:
    """Ultra-clean consumer manager"""
    
    def __init__(self):
        self.consumer = get_rabbitmq_consumer()
        self.service = get_service()
        self.registry = HandlerRegistry()
        self.thread: Optional[threading.Thread] = None
        self.running = False
        
        # Register handlers
        self.registry.register("user_lookup", UserLookupHandler(self.service, self.service))
    
    def start(self):
        """Start consumer"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True, name="Consumer")
        self.thread.start()
        logger.info("🚀 Consumer started")
    
    def stop(self):
        """Stop consumer"""
        if not self.running:
            return
        
        self.running = False
        self.consumer.stop_consuming()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        self.consumer.disconnect()
        logger.info("🛑 Consumer stopped")
    
    def _run(self):
        """Run consumer loop"""
        try:
            callback = create_user_lookup_callback(self._handle)
            self.consumer.setup_consumer(rabbitmq_config.user_lookup_request_queue, callback)
            
            while self.running:
                try:
                    self.consumer.start_consuming()
                except Exception as e:
                    if self.running:
                        logger.error(f"Consumer error: {e}")
                        import time
                        time.sleep(5)
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.running = False
    
    def _handle(self, data: dict) -> bool:
        """Handle message"""
        try:
            context = MessageContext(**{k: data.get(k, "") for k in ["request_id", "phone_or_email", "group_slug", "timestamp"]})
            handler = self.registry.get_handler("user_lookup")
            response = handler.handle(context)
            return self.service.publish(response)
        except Exception as e:
            logger.error(f"Handle error: {e}")
            return False


# Singleton
_manager = None

def get_manager() -> ConsumerManager:
    """Get singleton manager"""
    global _manager
    return _manager or (_manager := ConsumerManager())

def start_consumer():
    """Start consumer"""
    get_manager().start()

def stop_consumer():
    """Stop consumer"""
    get_manager().stop()