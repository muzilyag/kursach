from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_
from typing import List, Optional
import datetime

from src.core.database import get_db
from src.core.security import get_current_user
from src.schemas.content import ContentCreate, ViewingUpdate
from src.models.content import Content, Genre, CopyrightHolder, Tag
from src.models.user import User
from src.models.viewing import Viewing

router = APIRouter()

@router.get("")
async def get_content(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = Query(""),
    genre_ids: Optional[List[int]] = Query(None),
    tag_ids: Optional[List[int]] = Query(None),
    copyright_holder_ids: Optional[List[int]] = Query(None),
    sort: str = "content_id",
    order: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    
    query = select(Content).options(
        selectinload(Content.genres),
        selectinload(Content.copyright_holders),
        selectinload(Content.tags)
    )

    if search:
        search_filter = or_(
            Content.content_name.ilike(f"%{search}%"),
            Content.content_discription.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    if genre_ids:
        for g_id in genre_ids:
            query = query.where(Content.genres.any(Genre.genre_id == g_id))

    if tag_ids:
        for t_id in tag_ids:
            query = query.where(Content.tags.any(Tag.tag_id == t_id))

    if copyright_holder_ids:
        for c_id in copyright_holder_ids:
            query = query.where(Content.copyright_holders.any(CopyrightHolder.copyright_holder_id == c_id))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    col = getattr(Content, sort, Content.content_id)
    query = query.order_by(col.desc() if order == "desc" else col.asc())
    
    result = await db.execute(query.offset(offset).limit(limit))
    content_list = result.scalars().all()
    
    formatted_result = []
    for c in content_list:
        formatted_result.append({
            "content_id": c.content_id,
            "content_name": c.content_name,
            "content_type": c.content_type,
            "content_duration": str(c.content_duration),
            "content_publish_date": str(c.content_publish_date) if c.content_publish_date else None,
            "content_discription": c.content_discription,
            "genres": [{"genre_id": g.genre_id, "genre_name": g.genre_name} for g in c.genres],
            "tags": [{"tag_id": t.tag_id, "tag_name": t.tag_name} for t in c.tags],
            "copyright_holders": [
                {
                    "copyright_holder_id": h.copyright_holder_id, 
                    "copyright_holder_name": h.copyright_holder_name
                } for h in c.copyright_holders
            ]
        })
        
    return {
        "items": formatted_result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.post("")
async def create_content(data: ContentCreate, db: AsyncSession = Depends(get_db)):
    new_content = Content(
        content_name=data.content_name,
        content_type=data.content_type,
        content_duration=data.content_duration,
        content_publish_date=data.content_publish_date,
        content_discription=data.content_discription
    )
    
    if data.genre_ids:
        res = await db.execute(select(Genre).where(Genre.genre_id.in_(data.genre_ids)))
        new_content.genres = list(res.scalars().all())
        
    if data.copyright_holder_ids:
        res = await db.execute(select(CopyrightHolder).where(CopyrightHolder.copyright_holder_id.in_(data.copyright_holder_ids)))
        new_content.copyright_holders = list(res.scalars().all())
        
    if data.tag_ids:
        res = await db.execute(select(Tag).where(Tag.tag_id.in_(data.tag_ids)))
        new_content.tags = list(res.scalars().all())
        
    db.add(new_content)
    await db.commit()
    return {"success": True, "id": new_content.content_id}

@router.put("/{content_id}")
async def update_content(content_id: int, data: ContentCreate, db: AsyncSession = Depends(get_db)):
    query = select(Content).options(
        selectinload(Content.genres), 
        selectinload(Content.copyright_holders),
        selectinload(Content.tags)
    ).where(Content.content_id == content_id)
    
    content = (await db.execute(query)).scalar_one_or_none()
    if not content: 
        raise HTTPException(status_code=404, detail="Контент не найден")
    
    content.content_name = data.content_name
    content.content_type = data.content_type
    content.content_duration = data.content_duration
    content.content_publish_date = data.content_publish_date
    content.content_discription = data.content_discription
    
    if data.genre_ids is not None:
        if data.genre_ids:
            res = await db.execute(select(Genre).where(Genre.genre_id.in_(data.genre_ids)))
            content.genres = list(res.scalars().all())
        else:
            content.genres = []
        
    if data.copyright_holder_ids is not None:
        if data.copyright_holder_ids:
            res = await db.execute(select(CopyrightHolder).where(CopyrightHolder.copyright_holder_id.in_(data.copyright_holder_ids)))
            content.copyright_holders = list(res.scalars().all())
        else:
            content.copyright_holders = []

    if data.tag_ids is not None:
        if data.tag_ids:
            res = await db.execute(select(Tag).where(Tag.tag_id.in_(data.tag_ids)))
            content.tags = list(res.scalars().all())
        else:
            content.tags = []
        
    await db.commit()
    return {"success": True, "message": "Контент обновлен"}

@router.get("/{content_id}/progress")
async def get_viewing_progress(
    content_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Viewing).where(
        Viewing.user_id == current_user.user_id,
        Viewing.content_id == content_id
    )
    result = await db.execute(query)
    viewing = result.scalar_one_or_none()
    
    if not viewing:
        return {"progress": 0}
        
    return {"progress": viewing.viewing_progress}

@router.patch("/{content_id}/progress")
async def update_viewing_progress(
    content_id: int,
    data: ViewingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content_exists = await db.get(Content, content_id)
    if not content_exists:
        raise HTTPException(status_code=404, detail="Контент не найден")

    query = select(Viewing).where(
        Viewing.user_id == current_user.user_id,
        Viewing.content_id == content_id
    )
    result = await db.execute(query)
    viewing = result.scalar_one_or_none()

    now = datetime.datetime.now()

    if viewing:
        viewing.viewing_progress = data.progress
        viewing.viewing_finish = now
    else:
        viewing = Viewing(
            user_id=current_user.user_id,
            content_id=content_id,
            viewing_progress=data.progress,
            viewing_start=now,
            viewing_finish=now
        )
        db.add(viewing)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"success": True, "current_progress": data.progress}

@router.delete("/{content_id}")
async def delete_content(content_id: int, db: AsyncSession = Depends(get_db)):
    content = await db.get(Content, content_id)
    if not content: 
        raise HTTPException(status_code=404, detail="Контент не найден")
    await db.delete(content)
    await db.commit()
    return {"success": True, "message": "Контент удален"}

@router.get("/genres")
async def get_genres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Genre))
    return [{"genre_id": g.genre_id, "genre_name": g.genre_name} for g in result.scalars().all()]

@router.get("/copyright-holders")
async def get_copyright_holders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CopyrightHolder))
    return [{"copyright_holder_id": h.copyright_holder_id, "copyright_holder_name": h.copyright_holder_name} for h in result.scalars().all()]

@router.get("/tags")
async def get_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag))
    return [{"tag_id": t.tag_id, "tag_name": t.tag_name} for t in result.scalars().all()]