from fastapi import FastAPI
from db.database import Base, engine
from api.v1.routes import users, auth


Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service")

app.include_router(users.router)
app.include_router(auth.router)