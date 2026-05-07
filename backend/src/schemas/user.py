from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, Literal

class UserCreate(BaseModel):
    user_name: str
    user_email: EmailStr
    user_birth_date: date
    user_password: str
    user_role: Optional[Literal["user", "content_manager"]] = "user"
    user_registration_date: Optional[date] = None

class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[EmailStr] = None
    user_birth_date: Optional[date] = None
    user_password: Optional[str] = None
    user_registration_date: Optional[date] = None

class UserResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: EmailStr
    user_birth_date: date
    user_registration_date: date
    user_role: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    identifier: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"