from fastapi import FastAPI

from app.db.database import Base, engine
from app.api.v1.routes import users, auth, health
from app.rabbitmq.setup import init_rabbitmq

Base.metadata.create_all(bind=engine)

init_rabbitmq()

# Create FastAPI application
app = FastAPI(
    title="User Service",
    description="User management service with RabbitMQ integration",
    version="1.0.0"
)


app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)