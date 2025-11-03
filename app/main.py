import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
# Import models to ensure they're registered with Base
from app.models import user, otp_code, blacklisted_token
from app.api.v1.routes import users, auth, health
from app.rabbitmq.setup import init_rabbitmq
from app.redis.setup import init_redis
from app.services.user_lookup_consumer import start_consumer
from app.core.config import app_config

# Create FastAPI application
app = FastAPI(
    title="User Service",
    description="User management service with RabbitMQ and Redis integration",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    # Initialize database with retry logic
    max_retries = 5
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables created successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                print(f"⚠️  Warning: Failed to create database tables (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"   Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"⚠️  Warning: Failed to create database tables after {max_retries} attempts: {e}")
                print("   Application will continue but database operations may fail")
    
    # Initialize RabbitMQ
    init_rabbitmq()
    
    # Initialize Redis
    init_redis()
    
    # Start consumer
    try:
        start_consumer()
        print("✅ Consumer started")
    except Exception as e:
        print(f"⚠️ Consumer failed: {e}")

# Configure CORS middleware
# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)