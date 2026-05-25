from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import func, and_, exists, text
from datetime import date, timedelta
from typing import Optional
from src.core.database import get_db
from src.models.subscription import Subscribe, SubscribeType
from src.models.payment import Payment
from src.models.user import User
from src.schemas.subscription import (
    SubscriptionUpdate,
    SubscriptionChange,
    SubscriptionCreate,
    UserSubscriptionBuy,
)
from src.core.security import get_current_user, RoleChecker

router = APIRouter()

@router.get("/types", dependencies=[Depends(RoleChecker(["user", "admin", "superadmin"]))])
async def get_subscription_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SubscribeType))
    types = result.scalars().all()
    return [
        {
            "subscribe_type_id": t.subscribe_type_id,
            "subscribe_type_name": t.subscribe_type_name,
            "subscribe_type_discription": t.subscribe_type_discription,
            "subscribe_type_max_type_quality": t.subscribe_type_max_type_quality,
            "subscribe_type_cost": f"{float(t.subscribe_type_cost):.2f}",
            "subscribe_type_duration": t.subscribe_type_duration,
        }
        for t in types
    ]

@router.get(
    "/preview-change",
    dependencies=[
        Depends(RoleChecker(["user", "content_manager", "admin", "superadmin"]))
    ],
)
async def preview_subscription_change(
    target_type_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    active_sub_stmt = (
        select(Subscribe)
        .options(joinedload(Subscribe.subscribe_type))
        .where(
            and_(
                Subscribe.user_id == current_user.user_id,
                Subscribe.subscribe_finish >= date.today(),
            )
        )
        .order_by(Subscribe.subscribe_finish.desc())
        .limit(1)
    )

    active_sub_result = await db.execute(active_sub_stmt)
    active_sub = active_sub_result.scalar_one_or_none()

    target_type_result = await db.execute(
        select(SubscribeType).where(SubscribeType.subscribe_type_id == target_type_id)
    )
    target_type = target_type_result.scalar_one_or_none()

    if not target_type:
        raise HTTPException(status_code=404, detail="Целевой тариф не найден")

    base_cost = float(target_type.subscribe_type_cost)

    if not active_sub:
        return {
            "current_tariff_id": None,
            "target_tariff_id": target_type_id,
            "unused_days": 0,
            "discount_amount": "0.00",
            "final_payable_amount": f"{base_cost:.2f}",
        }

    if active_sub.subscribe_type_id == target_type_id:
        return {
            "current_tariff_id": active_sub.subscribe_type_id,
            "target_tariff_id": target_type_id,
            "unused_days": max(
                0, (active_sub.subscribe_finish - date.today()).days + 1
            ),
            "discount_amount": "0.00",
            "final_payable_amount": f"{base_cost:.2f}",
        }

    total_days = active_sub.subscribe_type.subscribe_type_duration
    total_cost = float(active_sub.subscribe_type.subscribe_type_cost)
    daily_cost = total_cost / total_days if total_days > 0 else 0

    unused_days = max(0, (active_sub.subscribe_finish - date.today()).days + 1)
    discount = unused_days * daily_cost
    final_amount = max(0.0, base_cost - discount)

    return {
        "current_tariff_id": active_sub.subscribe_type_id,
        "target_tariff_id": target_type_id,
        "unused_days": unused_days,
        "discount_amount": f"{discount:.2f}",
        "final_payable_amount": f"{final_amount:.2f}",
    }

@router.get(
    "/users-filtered", dependencies=[Depends(RoleChecker(["admin", "superadmin"]))]
)
async def get_users_filtered(
    has_active: bool, limit: int = 1000, db: AsyncSession = Depends(get_db)
):
    if has_active:
        query = (
            select(
                User.user_id,
                User.user_name,
                User.user_email,
                Subscribe.subscribe_type_id,
            )
            .join(Subscribe, Subscribe.user_id == User.user_id)
            .where(Subscribe.subscribe_finish >= date.today())
            .limit(limit)
        )
        result = await db.execute(query)
        return [
            {
                "user_id": r[0],
                "user_name": r[1],
                "user_email": r[2],
                "current_type_id": r[3],
            }
            for r in result.all()
        ]
    else:
        active_sub_exists = exists().where(
            and_(
                Subscribe.user_id == User.user_id,
                Subscribe.subscribe_finish >= date.today(),
            )
        )
        query = select(User).where(~active_sub_exists).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        return [
            {
                "user_id": u.user_id,
                "user_name": u.user_name,
                "user_email": u.user_email,
                "current_type_id": None,
            }
            for u in users
        ]

@router.get("", dependencies=[Depends(RoleChecker(["admin", "superadmin"]))])
async def get_subscriptions(
    page: int = 1,
    limit: int = 10,
    search: str = "",
    sort: str = "subscribe_start",
    order: str = "desc",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    show_expired: bool = False,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit
    query = (
        select(Subscribe)
        .options(selectinload(Subscribe.user), selectinload(Subscribe.subscribe_type))
        .join(User, Subscribe.user_id == User.user_id)
        .join(
            SubscribeType,
            Subscribe.subscribe_type_id == SubscribeType.subscribe_type_id,
        )
    )

    conditions = []
    if search:
        conditions.append(User.user_name.ilike(f"%{search}%"))
    if start_date:
        conditions.append(Subscribe.subscribe_start >= start_date)
    if end_date:
        conditions.append(Subscribe.subscribe_start <= end_date)
    if not show_expired:
        conditions.append(Subscribe.subscribe_finish >= date.today())

    if conditions:
        query = query.where(and_(*conditions))

    if sort == "user_name":
        col = User.user_name
    elif sort == "subscribe_type_name":
        col = SubscribeType.subscribe_type_name
    else:
        col = getattr(Subscribe, sort, Subscribe.subscribe_start)

    query = query.order_by(col.desc() if order == "desc" else col.asc())
    result = await db.execute(query.offset(offset).limit(limit))
    subs_list = result.scalars().all()

    count_query = select(func.count()).select_from(Subscribe).join(User)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = (await db.execute(count_query)).scalar()

    formatted_result = []
    for s in subs_list:
        formatted_result.append(
            {
                "user_id": s.user_id,
                "subscribe_type_id": s.subscribe_type_id,
                "subscribe_start": str(s.subscribe_start),
                "subscribe_finish": str(s.subscribe_finish)
                if s.subscribe_finish
                else None,
                "status": "Активна"
                if s.subscribe_finish and s.subscribe_finish >= date.today()
                else "Истекла",
                "user": {
                    "user_id": s.user.user_id,
                    "user_name": s.user.user_name,
                    "user_email": s.user.user_email,
                }
                if s.user
                else None,
                "subscribe_type": {
                    "subscribe_type_id": s.subscribe_type.subscribe_type_id,
                    "subscribe_type_name": s.subscribe_type.subscribe_type_name,
                    "subscribe_type_cost": f"{float(s.subscribe_type.subscribe_type_cost):.2f}",
                }
                if s.subscribe_type
                else None,
            }
        )

    return {
        "subscriptions": formatted_result,
        "items": formatted_result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }

@router.post("", dependencies=[Depends(RoleChecker(["admin", "superadmin"]))])
async def create_subscription(
    data: SubscriptionCreate, db: AsyncSession = Depends(get_db)
):
    active_sub_check = await db.execute(
        select(1).where(
            and_(
                Subscribe.user_id == data.user_id,
                Subscribe.subscribe_finish >= date.today(),
            )
        )
    )
    if active_sub_check.scalar():
        raise HTTPException(
            status_code=400, detail="У пользователя уже есть активная подписка"
        )

    type_result = await db.execute(
        select(SubscribeType).where(
            SubscribeType.subscribe_type_id == data.subscribe_type_id
        )
    )
    sub_type = type_result.scalar_one_or_none()
    if not sub_type:
        raise HTTPException(status_code=404, detail="Тип подписки не найден")

    start_date = (
        data.user_registration_date
        if hasattr(data, "user_registration_date")
        else date.today()
    )

    existing_sub_query = select(Subscribe).where(
        and_(
            Subscribe.user_id == data.user_id,
            Subscribe.subscribe_type_id == data.subscribe_type_id,
            Subscribe.subscribe_start == start_date,
        )
    )
    existing_sub_result = await db.execute(existing_sub_query)
    existing_sub = existing_sub_result.scalar_one_or_none()

    if existing_sub:
        existing_sub.subscribe_finish = data.subscribe_finish
    else:
        sub = Subscribe(
            user_id=data.user_id,
            subscribe_type_id=data.subscribe_type_id,
            subscribe_start=start_date,
            subscribe_finish=data.subscribe_finish,
        )
        db.add(sub)

    await db.flush()

    max_pn_result = await db.execute(
        select(func.max(Payment.payment_number)).where(Payment.user_id == data.user_id)
    )
    max_pn = max_pn_result.scalar() or 0

    payment = Payment(
        user_id=data.user_id,
        payment_number=max_pn + 1,
        subscribe_type_id=data.subscribe_type_id,
        subscribe_start=start_date,
        payment_date=date.today(),
        payment_sum=sub_type.subscribe_type_cost,
        payment_method="карта",
    )

    db.add(payment)

    try:
        await db.commit()
        return {"success": True}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change", dependencies=[Depends(RoleChecker(["user", "admin", "superadmin"]))])
async def change_subscription(
    data: SubscriptionChange, db: AsyncSession = Depends(get_db)
):
    try:
        await db.execute(
            text("CALL change_subscription_type(:u_id, :t_id, :p_method)"),
            {
                "u_id": data.user_id,
                "t_id": data.subscribe_type_id,
                "p_method": data.payment_method,
            },
        )
        await db.commit()
        return {"success": True}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put(
    "/{user_id}/{type_id}/{start_date}",
    dependencies=[Depends(RoleChecker(["user", "superadmin"]))],
)
async def update_subscription(
    user_id: int,
    type_id: int,
    start_date: date,
    data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
):
    query = select(Subscribe).where(
        and_(
            Subscribe.user_id == user_id,
            Subscribe.subscribe_type_id == type_id,
            Subscribe.subscribe_start == start_date,
        )
    )
    result = await db.execute(query)
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найден")

    sub.subscribe_finish = data.subscribe_finish
    await db.commit()
    return {"success": True}

@router.patch(
    "/{user_id}/{type_id}/{start_date}/cancel",
    dependencies=[Depends(RoleChecker(["user", "admin", "superadmin"]))],
)
async def cancel_subscription(
    user_id: int, type_id: int, start_date: date, db: AsyncSession = Depends(get_db)
):
    query = select(Subscribe).where(
        and_(
            Subscribe.user_id == user_id,
            Subscribe.subscribe_type_id == type_id,
            Subscribe.subscribe_start == start_date,
        )
    )
    result = await db.execute(query)
    sub = result.scalar_one_or_none()

    if not sub:
        raise HTTPException(status_code=404, detail="Подписка не найдена")

    sub.subscribe_finish = date.today() - timedelta(days=1)
    await db.commit()
    return {"success": True}

@router.post("/buy", dependencies=[Depends(RoleChecker(["user", "superadmin"]))])
async def buy_subscription_self_service(
    data: UserSubscriptionBuy,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    active_sub_stmt = (
        select(Subscribe)
        .where(
            and_(
                Subscribe.user_id == current_user.user_id,
                Subscribe.subscribe_finish >= date.today(),
            )
        )
        .order_by(Subscribe.subscribe_finish.desc())
        .limit(1)
    )

    active_sub_result = await db.execute(active_sub_stmt)
    active_sub = active_sub_result.scalar_one_or_none()

    type_result = await db.execute(
        select(SubscribeType).where(
            SubscribeType.subscribe_type_id == data.subscribe_type_id
        )
    )
    sub_type = type_result.scalar_one_or_none()
    if not sub_type:
        raise HTTPException(status_code=404, detail="Тариф не найден")

    start_date = date.today()
    if active_sub:
        if active_sub.subscribe_type_id == data.subscribe_type_id:
            start_date = active_sub.subscribe_finish + timedelta(days=1)
        else:
            raise HTTPException(
                status_code=400,
                detail="У вас есть активная подписка другого типа. Используйте смену тарифа.",
            )

    finish_date = start_date + timedelta(days=sub_type.subscribe_type_duration)

    existing_sub_query = select(Subscribe).where(
        and_(
            Subscribe.user_id == current_user.user_id,
            Subscribe.subscribe_type_id == data.subscribe_type_id,
            Subscribe.subscribe_start == start_date,
        )
    )
    existing_sub_result = await db.execute(existing_sub_query)
    existing_sub = existing_sub_result.scalar_one_or_none()

    if existing_sub:
        existing_sub.subscribe_finish = finish_date
    else:
        sub = Subscribe(
            user_id=current_user.user_id,
            subscribe_type_id=data.subscribe_type_id,
            subscribe_start=start_date,
            subscribe_finish=finish_date,
        )
        db.add(sub)

    await db.flush()

    max_pn_result = await db.execute(
        select(func.max(Payment.payment_number)).where(
            Payment.user_id == current_user.user_id
        )
    )
    max_pn = max_pn_result.scalar() or 0

    payment = Payment(
        user_id=current_user.user_id,
        payment_number=max_pn + 1,
        subscribe_type_id=data.subscribe_type_id,
        subscribe_start=start_date,
        payment_date=date.today(),
        payment_sum=sub_type.subscribe_type_cost,
        payment_method=data.payment_method,
    )
    db.add(payment)

    try:
        await db.commit()
        return {"success": True, "expires_at": str(finish_date)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))