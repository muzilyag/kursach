from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from src.core.database import get_db
from src.models.user import User
from src.models.content import Content, Genre, CopyrightHolder, Tag
from src.models.payment import Payment
from src.models.viewing import Viewing
from src.core.security import get_current_user

router = APIRouter()

@router.get("")
async def get_dashboard_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора."
        )

    users_query = await db.execute(select(func.count(User.user_id)))
    total_users = users_query.scalar() or 0

    revenue_query = await db.execute(select(func.sum(Payment.payment_sum)))
    total_revenue = revenue_query.scalar() or 0.0

    content_query = await db.execute(select(func.count(Content.content_id)))
    total_content = content_query.scalar() or 0

    genres_query = await db.execute(select(func.count(Genre.genre_id)))
    total_genres = genres_query.scalar() or 0

    holders_query = await db.execute(select(func.count(CopyrightHolder.copyright_holder_id)))
    total_copyright_holders = holders_query.scalar() or 0

    tags_query = await db.execute(select(func.count(Tag.tag_id)))
    total_tags = tags_query.scalar() or 0

    viewings_query = await db.execute(select(func.count()).select_from(Viewing))
    total_viewings = viewings_query.scalar() or 0

    content_types_query = await db.execute(
        select(Content.content_type, func.count(Content.content_id))
        .group_by(Content.content_type)
    )
    content_types_breakdown = [
        {"type": row[0], "count": row[1]} for row in content_types_query.all()
    ]

    payment_methods_query = await db.execute(
        select(Payment.payment_method, func.sum(Payment.payment_sum))
        .group_by(Payment.payment_method)
    )
    payment_methods_breakdown = [
        {"method": row[0], "amount": f"{float(row[1]):.2f}"} for row in payment_methods_query.all()
    ]

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
            "payment_methods": payment_methods_breakdown
        }
    }