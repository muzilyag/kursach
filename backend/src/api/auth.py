from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.core.database import get_db
from src.core.security import get_password_hash, verify_password, create_access_token
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(
        or_(User.user_email == user_data.user_email, User.user_name == user_data.user_name)
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email или именем уже существует"
        )

    new_user = User(
        user_name=user_data.user_name,
        user_email=user_data.user_email,
        user_birth_date=user_data.user_birth_date,
        user_password=get_password_hash(user_data.user_password),
        user_role=user_data.user_role,
        user_registration_date=user_data.user_registration_date or datetime.now().date()
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка целостности данных")
    
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(
        or_(User.user_email == credentials.identifier, User.user_name == credentials.identifier)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    access_token = create_access_token(data={"sub": str(user.user_id), "role": user.user_role})
    
    return TokenResponse(access_token=access_token) 