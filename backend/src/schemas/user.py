from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    user_name: str
    user_email: EmailStr
    user_birth_date: date
    user_registration_date: Optional[date] = None

class UserUpdate(BaseModel):
    user_name: str
    user_email: EmailStr
    user_birth_date: date
    user_registration_date: Optional[date] = None

class UserResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: EmailStr
    user_birth_date: date
    user_registration_date: date

    class Config:
        from_attributes = True