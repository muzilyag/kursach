from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
from src.core.database import get_db
from src.repositories.subscription_repository import SubscriptionRepository

router = APIRouter()

@router.get("")
async def get_subscriptions(
    page: int = 1,
    limit: int = 10,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    repo = SubscriptionRepository(db)
    subscriptions, total = await repo.get_subscriptions(page, limit, start_date, end_date)
    
    return {
        "subscriptions": subscriptions,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "filter": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }

@router.get("/types")
async def get_subscription_types(db: AsyncSession = Depends(get_db)):
    repo = SubscriptionRepository(db)
    return await repo.get_subscription_types()