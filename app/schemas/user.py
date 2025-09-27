from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    full_name: str 
    email: EmailStr
    username: str  
    phone_number: str | None = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str  
    token_type: str 


class PasswordReset(BaseModel):
    email: EmailStr