from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.core.database import get_db
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate
from src.models.user import User

router = APIRouter()

@router.get("")
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

@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.post("")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    new_user = User(**user_data.model_dump())
    try:
        created = await repo.create(new_user)
        return {
            "success": True, 
            "message": "Пользователь добавлен", 
            "user": created
        }
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

@router.put("/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    try:
        updated = await repo.update(user_id, user_data.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {
            "success": True, 
            "message": "Пользователь обновлен", 
            "user": updated
        }
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {
        "success": True, 
        "message": "Пользователь и все связанные данные удалены"
    }