from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from src.core.database import get_db
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.models.user import User
from src.core.security import RoleChecker, get_password_hash, get_current_user

router = APIRouter()

@router.get("", dependencies=[Depends(RoleChecker(["admin"]))])
async def get_users(page: int = 1, limit: int = 10, search: str = "", sort: str = "user_id", order: str = "asc", db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    users = await repo.get_all(page, limit, search, sort, order)
    total = await repo.get_count(search)
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "sort": sort,
        "order": order
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.post("", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user_dict = user_data.model_dump()
    user_dict["user_password"] = get_password_hash(user_dict["user_password"])
    
    new_user = User(**user_dict)
    try:
        created = await repo.create(new_user)
        return {
            "success": True, 
            "message": "Пользователь добавлен", 
            "user": created
        }
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

@router.put("/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    update_dict = user_data.model_dump(exclude_unset=True)
    
    if "user_password" in update_dict:
        update_dict["user_password"] = get_password_hash(update_dict["user_password"])
        
    try:
        updated = await repo.update(user_id, update_dict)
        if not updated:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {
            "success": True, 
            "message": "Пользователь обновлен", 
            "user": updated
        }
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

@router.delete("/{user_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {
        "success": True, 
        "message": "Пользователь и все связанные данные удалены"
    }