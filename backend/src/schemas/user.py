from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from typing import Optional, Literal

class UserActiveSubSchema(BaseModel):
    subscribe_type_id: int
    subscribe_type_name: str
    subscribe_start: date
    subscribe_finish: date
    status: str

class UserCreate(BaseModel):
    user_name: str
    user_email: EmailStr
    user_birth_date: date
    user_password: str
    user_role: Optional[Literal["user", "content_manager", "admin"]] = "user"
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
    active_subscription: Optional[UserActiveSubSchema] = None
    had_subscription: bool = False
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    identifier: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str