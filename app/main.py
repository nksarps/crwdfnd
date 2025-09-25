from app.routers import user
from app.config.database import init_db

from fastapi import FastAPI

app = FastAPI()

app.include_router(user.router)