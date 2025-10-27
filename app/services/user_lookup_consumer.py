import logging
import threading
from typing import Optional
from app.rabbitmq.consumer import get_rabbitmq_consumer, create_user_lookup_callback
from app.rabbitmq.config import rabbitmq_config
from app.services.user_lookup_service import get_user_lookup_service

logger = logging.getLogger(__name__)


class UserLookupConsumerManager:
    """Manages background RabbitMQ consumer for user lookup requests"""
    
    def __init__(self):
        self.consumer_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.consumer = get_rabbitmq_consumer()
        self.user_lookup_service = get_user_lookup_service()
    
    def start_user_lookup_consumer(self):
        """Start the user lookup consumer in a separate thread"""
        if self.is_running:
            logger.warning("User lookup consumer is already running")
            return
        
        self.is_running = True
        self.consumer_thread = threading.Thread(
            target=self._run_user_lookup_consumer,
            daemon=True,
            name="UserLookup-Consumer"
        )
        self.consumer_thread.start()
        logger.info("User lookup consumer started")
    
    def stop_user_lookup_consumer(self):
        """Stop the user lookup consumer"""
        if not self.is_running:
            logger.warning("User lookup consumer is not running")
            return
        
        self.is_running = False
        
        # Stop consuming messages
        self.consumer.stop_consuming()
        
        # Wait for thread to finish
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5)
            if self.consumer_thread.is_alive():
                logger.warning("User lookup consumer thread did not stop gracefully")
        
        # Disconnect from RabbitMQ
        self.consumer.disconnect()
        
        logger.info("User lookup consumer stopped")
    
    def _run_user_lookup_consumer(self):
        """Run the user lookup consumer in the background thread"""
        try:
            logger.info("Starting user lookup consumer loop")
            
            # Setup consumer for user lookup requests
            callback = create_user_lookup_callback(self._handle_user_lookup_request)
            self.consumer.setup_consumer(rabbitmq_config.user_lookup_request_queue, callback)
            
            while self.is_running:
                try:
                    # Start consuming messages
                    self.consumer.start_consuming()
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Error in user lookup consumer loop: {e}")
                        # Wait a bit before retrying
                        import time
                        time.sleep(5)
                    else:
                        logger.info("User lookup consumer loop stopped")
                        break
        except Exception as e:
            logger.error(f"Fatal error in user lookup consumer: {e}")
        finally:
            self.is_running = False
            logger.info("User lookup consumer thread finished")
    
    def _handle_user_lookup_request(self, message_data: dict) -> bool:
        """
        Handle user lookup request message
        
        Args:
            message_data: Message data containing phone_or_email, request_id, group_slug
            
        Returns:
            bool: True if processed successfully, False otherwise
        """
        try:
            phone_or_email = message_data.get("phone_or_email")
            request_id = message_data.get("request_id")
            group_slug = message_data.get("group_slug")
            
            if not phone_or_email or not request_id:
                logger.error("❌ Invalid user lookup request: missing phone_or_email or request_id")
                return False
            
            logger.info(f"🔍 CONSUMING MESSAGE: Request ID {request_id}")
            logger.info(f"   📞 Phone/Email: {phone_or_email}")
            logger.info(f"   🏷️  Group Slug: {group_slug}")
            logger.info(f"   ⏰ Timestamp: {message_data.get('timestamp', 'N/A')}")
            
            # Look up user
            logger.info(f"🔎 Looking up user in database...")
            user_data = self.user_lookup_service.lookup_user_by_phone_or_email(phone_or_email)
            
            # Publish response
            if user_data:
                logger.info(f"✅ USER FOUND!")
                logger.info(f"   👤 User ID: {user_data.get('user_id')}")
                logger.info(f"   📛 Name: {user_data.get('name')}")
                logger.info(f"   📞 Phone: {user_data.get('phone_number')}")
                logger.info(f"   📧 Email: {user_data.get('email')}")
                logger.info(f"   🔑 Role: {user_data.get('role')}")
                
                success = self.user_lookup_service.publish_user_lookup_response(
                    request_id=request_id,
                    success=True,
                    user_data=user_data
                )
                
                if success:
                    logger.info(f"📤 RESPONSE PUBLISHED: Success response sent for {phone_or_email}")
                else:
                    logger.error(f"❌ FAILED TO PUBLISH: Success response failed for {phone_or_email}")
            else:
                logger.info(f"❌ USER NOT FOUND: No user found with {phone_or_email}")
                
                success = self.user_lookup_service.publish_user_lookup_response(
                    request_id=request_id,
                    success=False,
                    error_message=f"User not found with {phone_or_email}"
                )
                
                if success:
                    logger.info(f"📤 RESPONSE PUBLISHED: Not found response sent for {phone_or_email}")
                else:
                    logger.error(f"❌ FAILED TO PUBLISH: Not found response failed for {phone_or_email}")
            
            logger.info(f"🏁 PROCESSING COMPLETE: Request {request_id} - Success: {success}")
            return success
            
        except Exception as e:
            logger.error(f"💥 ERROR handling user lookup request: {e}")
            # Try to publish error response
            try:
                request_id = message_data.get("request_id")
                if request_id:
                    logger.info(f"📤 PUBLISHING ERROR RESPONSE for request {request_id}")
                    self.user_lookup_service.publish_user_lookup_response(
                        request_id=request_id,
                        success=False,
                        error_message=f"Processing error: {str(e)}"
                    )
                    logger.info(f"📤 ERROR RESPONSE PUBLISHED for request {request_id}")
            except Exception as publish_error:
                logger.error(f"❌ FAILED TO PUBLISH ERROR RESPONSE: {publish_error}")
            return False


# Global user lookup consumer manager
_user_lookup_consumer_manager: Optional[UserLookupConsumerManager] = None


def get_user_lookup_consumer_manager() -> UserLookupConsumerManager:
    """Get or create user lookup consumer manager instance"""
    global _user_lookup_consumer_manager
    if _user_lookup_consumer_manager is None:
        _user_lookup_consumer_manager = UserLookupConsumerManager()
    return _user_lookup_consumer_manager


def start_user_lookup_consumer():
    """Start the user lookup consumer"""
    manager = get_user_lookup_consumer_manager()
    manager.start_user_lookup_consumer()


def stop_user_lookup_consumer():
    """Stop the user lookup consumer"""
    manager = get_user_lookup_consumer_manager()
    manager.stop_user_lookup_consumer()
