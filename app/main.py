from fastapi import FastAPI

from app.db.database import Base, engine
from app.api.v1.routes import users, auth, health
from app.rabbitmq.setup import init_rabbitmq
from app.redis.setup import init_redis
from app.services.user_lookup_consumer import start_user_lookup_consumer

# Initialize database with error handling
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Warning: Failed to create database tables: {e}")
    print("   Application will continue but database operations may fail")

init_rabbitmq()
init_redis()

# Start user lookup consumer with error handling
try:
    start_user_lookup_consumer()
    print("✅ User lookup consumer started successfully")
except Exception as e:
    print(f"⚠️  Warning: Failed to start user lookup consumer: {e}")
    print("   Application will continue without user lookup functionality")

# Create FastAPI application
app = FastAPI(
    title="User Service",
    description="User management service with RabbitMQ and Redis integration",
    version="1.0.0"
)


app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)