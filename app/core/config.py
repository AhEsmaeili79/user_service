import os
from typing import Optional
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration settings"""

    db_name: str = os.getenv("POSTGRES_DB")
    db_user: str = os.getenv("POSTGRES_USER")
    db_password: str = os.getenv("POSTGRES_PASSWORD")
    db_host: str = "postgres"
    db_port: int = 5432
    database_url: str = os.getenv("DATABASE_URL")

    class Config:
        env_file = ".env"
        case_sensitive = False


class RedisConfig(BaseSettings):
    """Redis configuration settings"""

    host: str = os.getenv("REDIS_HOST", "redis")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    password: str = os.getenv("REDIS_PASSWORD")
    db: int = int(os.getenv("REDIS_DB", "0"))
    max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
    socket_timeout: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    socket_connect_timeout: int = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))

    # Redis URL for connection
    @property
    def redis_url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"

    class Config:
        env_file = ".env"
        case_sensitive = False


class RabbitMQConfig(BaseSettings):
    """RabbitMQ configuration settings"""

    # Connection settings
    host: str = os.getenv("RABBITMQ_HOST")
    port: int = int(os.getenv("RABBITMQ_PORT"))
    username: str = os.getenv("RABBITMQ_USERNAME")
    password: str = os.getenv("RABBITMQ_PASSWORD")
    virtual_host: str = os.getenv("RABBITMQ_VHOST")

    # Connection pool settings
    connection_attempts: int = int(os.getenv("RABBITMQ_CONNECTION_ATTEMPTS", "3"))
    retry_delay: float = float(os.getenv("RABBITMQ_RETRY_DELAY", "2.0"))
    heartbeat: int = int(os.getenv("RABBITMQ_HEARTBEAT", "600"))

    # Exchange settings
    otp_exchange: str = "user.otp.exchange"
    exchange_type: str = "topic"

    # Queue settings
    email_queue: str = "user.otp.email.queue"
    sms_queue: str = "user.otp.sms.queue"

    # Routing keys
    email_routing_key: str = "otp.email.send"
    sms_routing_key: str = "otp.sms.send"

    # Message settings
    message_ttl: int = int(os.getenv("RABBITMQ_MESSAGE_TTL", "300000"))  # 5 minutes in milliseconds

    class Config:
        env_file = ".env"
        case_sensitive = False


class JWTConfig(BaseSettings):
    """JWT configuration settings"""

    secret_key: str = os.getenv("SECRET_KEY")
    refresh_secret_key: str = os.getenv("REFRESH_SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    class Config:
        env_file = ".env"
        case_sensitive = False


class AppConfig(BaseSettings):
    """Application configuration settings"""

    pythonpath: Optional[str] = os.getenv("PYTHONPATH")
    # CORS Settings - comma-separated list of allowed origins
    cors_origins: Optional[str] = os.getenv("CORS_ORIGINS", "*")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global config instances
database_config = DatabaseConfig()
redis_config = RedisConfig()
rabbitmq_config = RabbitMQConfig()
jwt_config = JWTConfig()
app_config = AppConfig()