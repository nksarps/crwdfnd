from .base import BaseModel

from sqlalchemy import Column, String, Boolean


class User(BaseModel):
    __tablename__ = "users"

    full_name = Column(String(length=100), nullable=False)
    email = Column(String(length=100), unique=True, nullable=False)
    username = Column(String(length=100), unique=True, nullable=False)
    phone_number = Column(String(length=100), unique=True, nullable=True)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)