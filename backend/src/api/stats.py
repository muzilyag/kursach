from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.repositories.stats_repository import StatsRepository

router = APIRouter()

@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    repo = StatsRepository(db)
    try:
        return await repo.get_dashboard_stats()
    except Exception as e:
        print(f"Ошибка загрузки статистики: {e}")
        return {
            "users": 0, 
            "content": 0, 
            "totalSubscriptions": 0,
            "activeSubscriptions": 0, 
            "views": 0, 
            "totalRevenue": 0.0
        }

@router.get("/debug/tables")
async def get_tables_structure(db: AsyncSession = Depends(get_db)):
    repo = StatsRepository(db)
    try:
        return await repo.get_tables_structure()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))