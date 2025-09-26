from fastapi import FastAPI

from app.db.database import Base, engine
from app.api.v1.routes import users, auth, health
from app.rabbitmq.setup import init_rabbitmq
from app.redis.setup import init_redis

Base.metadata.create_all(bind=engine)

init_rabbitmq()
init_redis()

# Create FastAPI application
app = FastAPI(
    title="User Service",
    description="User management service with RabbitMQ and Redis integration",
    version="1.0.0"
)


app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)