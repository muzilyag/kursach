import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, not_
from src.core.database import get_db
from src.models.user import User
from src.models.content import Content, Genre, CopyrightHolder, Tag
from src.models.payment import Payment
from src.models.viewing import Viewing
from src.models.subscription import Subscribe, SubscribeType
from src.core.security import get_current_user, RoleChecker

router = APIRouter()


@router.get("", dependencies=[Depends(RoleChecker(["admin", "superadmin"]))])
async def get_dashboard_statistics(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if current_user.user_role != "admin" and current_user.user_role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора.",
        )

    users_query = await db.execute(
        select(func.count(User.user_id)).where(not_(User.user_email.endswith("@deleted.local")))
    )
    total_users = users_query.scalar() or 0

    revenue_query = await db.execute(select(func.sum(Payment.payment_sum)))
    total_revenue = revenue_query.scalar() or 0.0

    content_query = await db.execute(select(func.count(Content.content_id)))
    total_content = content_query.scalar() or 0

    genres_query = await db.execute(select(func.count(Genre.genre_id)))
    total_genres = genres_query.scalar() or 0

    holders_query = await db.execute(
        select(func.count(CopyrightHolder.copyright_holder_id))
    )
    total_copyright_holders = holders_query.scalar() or 0

    tags_query = await db.execute(select(func.count(Tag.tag_id)))
    total_tags = tags_query.scalar() or 0

    viewings_query = await db.execute(select(func.count()).select_from(Viewing))
    total_viewings = viewings_query.scalar() or 0

    content_types_query = await db.execute(
        select(Content.content_type, func.count(Content.content_id)).group_by(
            Content.content_type
        )
    )
    content_types_breakdown = [
        {"type": row[0], "count": row[1]} for row in content_types_query.all()
    ]

    payment_methods_query = await db.execute(
        select(Payment.payment_method, func.sum(Payment.payment_sum)).group_by(
            Payment.payment_method
        )
    )
    payment_methods_breakdown = [
        {"method": row[0], "amount": f"{float(row[1]):.2f}"}
        for row in payment_methods_query.all()
    ]

    today = datetime.date.today()

    active_subs_query = await db.execute(
        select(func.count(Subscribe.user_id)).where(Subscribe.subscribe_finish >= today)
    )
    active_subs = active_subs_query.scalar() or 0

    expired_subs_query = await db.execute(
        select(func.count(Subscribe.user_id)).where(Subscribe.subscribe_finish < today)
    )
    expired_subs = expired_subs_query.scalar() or 0

    tariffs_query = await db.execute(
        select(
            SubscribeType.subscribe_type_name,
            func.sum(Payment.payment_sum),
            func.count(Payment.payment_number),
        )
        .join(Payment, SubscribeType.subscribe_type_id == Payment.subscribe_type_id)
        .group_by(SubscribeType.subscribe_type_name)
    )
    revenue_by_tariffs = [
        {
            "tariff_name": row[0],
            "amount": f"{float(row[1]):.2f}" if row[1] is not None else "0.00",
            "count": row[2],
        }
        for row in tariffs_query.all()
    ]

    start_this_week = today - datetime.timedelta(days=6)
    start_past_week = today - datetime.timedelta(days=13)
    end_past_week = today - datetime.timedelta(days=7)

    this_week_query = await db.execute(
        select(func.count(User.user_id)).where(
            User.user_registration_date >= start_this_week,
            not_(User.user_email.endswith("@deleted.local"))
        )
    )
    total_new_this_week = this_week_query.scalar() or 0

    past_week_query = await db.execute(
        select(func.count(User.user_id)).where(
            User.user_registration_date >= start_past_week,
            User.user_registration_date <= end_past_week,
            not_(User.user_email.endswith("@deleted.local"))
        )
    )
    total_new_past_week = past_week_query.scalar() or 0

    if total_new_past_week == 0:
        growth_percentage = 0.0
    else:
        growth_percentage = round(
            ((total_new_this_week - total_new_past_week) / total_new_past_week) * 100, 1
        )

    daily_query = await db.execute(
        select(User.user_registration_date, func.count(User.user_id))
        .where(
            User.user_registration_date >= start_this_week,
            not_(User.user_email.endswith("@deleted.local"))
        )
        .group_by(User.user_registration_date)
    )
    daily_counts = {row[0]: row[1] for row in daily_query.all()}

    daily_dynamics = []
    for i in range(7):
        current_day = start_this_week + datetime.timedelta(days=i)
        daily_dynamics.append(
            {
                "date": current_day.strftime("%Y-%m-%d"),
                "count": daily_counts.get(current_day, 0),
            }
        )

    return {
        "total_users": total_users,
        "total_revenue": f"{float(total_revenue):.2f}",
        "total_content": total_content,
        "total_genres": total_genres,
        "total_copyright_holders": total_copyright_holders,
        "total_tags": total_tags,
        "total_viewings": total_viewings,
        "breakdown": {
            "content_types": content_types_breakdown,
            "payment_methods": payment_methods_breakdown,
            "subscriptions_status": {"active": active_subs, "expired": expired_subs},
            "revenue_by_tariffs": revenue_by_tariffs,
            "registrations_dynamics": {
                "total_new_this_week": total_new_this_week,
                "growth_percentage": growth_percentage,
                "daily": daily_dynamics,
            },
        },
    }