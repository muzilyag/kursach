from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, and_
from datetime import date
from typing import Optional
from src.core.database import get_db
from src.models.subscription import Subscribe, SubscribeType
from src.models.user import User

router = APIRouter()

@router.get("")
async def get_subscriptions(
    page: int = 1,
    limit: int = 10,
    search: str = "",
    sort: str = "subscribe_start",
    order: str = "desc",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit

    query = select(Subscribe).options(
        selectinload(Subscribe.user),
        selectinload(Subscribe.subscribe_type)
    ).join(User, Subscribe.user_id == User.user_id)\
     .join(SubscribeType, Subscribe.subscribe_type_id == SubscribeType.subscribe_type_id)

    conditions = []
    if search:
        conditions.append(User.user_name.ilike(f"%{search}%"))
    if start_date:
        conditions.append(Subscribe.subscribe_start >= start_date)
    if end_date:
        conditions.append(Subscribe.subscribe_finish <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    if sort == "user_name":
        col = User.user_name
    elif sort == "subscribe_type_name":
        col = SubscribeType.subscribe_type_name
    else:
        col = getattr(Subscribe, sort, Subscribe.subscribe_start)

    if order == "desc":
        query = query.order_by(col.desc())
    else:
        query = query.order_by(col.asc())

    result = await db.execute(query.offset(offset).limit(limit))
    subs_list = result.scalars().all()

    count_query = select(func.count()).select_from(Subscribe).join(User)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = (await db.execute(count_query)).scalar()

    formatted_result = []
    for s in subs_list:
        formatted_result.append({
            "user_id": s.user_id,
            "subscribe_type_id": s.subscribe_type_id,
            "Пользователь": s.user.user_name if s.user else "Неизвестен",
            "Тип подписки": s.subscribe_type.subscribe_type_name if s.subscribe_type else "Неизвестен",
            "Дата начала": str(s.subscribe_start),
            "Дата окончания": str(s.subscribe_finish) if s.subscribe_finish else None,
            "Статус": "Активна" if s.subscribe_finish >= date.today() else "Истекла"
        })

    return {
        "subscriptions": formatted_result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "sort": sort,
        "order": order,
        "filter": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }

@router.get("/types")
async def get_subscription_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SubscribeType))
    types = result.scalars().all()
    
    return [{
        "id": t.subscribe_type_id,
        "name": t.subscribe_type_name,
        "cost": t.subscribe_type_cost,
        "duration": t.subscribe_type_duration
    } for t in types]