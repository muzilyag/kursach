from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from src.core.database import get_db
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from src.models.user import User
from src.core.security import RoleChecker, get_password_hash, get_current_user, verify_password

router = APIRouter()

@router.get("", dependencies=[Depends(RoleChecker(["admin"]))])
async def get_users(
    page: int = 1, 
    limit: int = 10, 
    search: str = "", 
    sort: str = "user_id", 
    order: str = "asc", 
    roles: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    users = await repo.get_all(page, limit, search, sort, order, roles)
    total = await repo.get_count(search, roles)
    
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

@router.patch("/me", response_model=UserResponse)
async def patch_me(
    user_data: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    update_dict = user_data.model_dump(exclude_unset=True)
    
    if "user_password" in update_dict:
        update_dict["user_password"] = get_password_hash(update_dict["user_password"])
    
    if current_user.user_role != "admin":
        update_dict.pop("user_role", None)
        update_dict.pop("user_registration_date", None)

    updated = await repo.update(current_user.user_id, update_dict)
    return updated

@router.patch("/me/password")
async def change_password(
    data: UserPasswordUpdate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(data.old_password, current_user.user_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный старый пароль"
        )
    
    new_hash = get_password_hash(data.new_password)
    repo = UserRepository(db)
    await repo.update(current_user.user_id, {"user_password": new_hash})
    
    return {"success": True, "message": "Пароль успешно изменен"}

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