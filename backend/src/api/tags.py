from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from sqlalchemy import select, delete, desc, asc, func
from src.core.database import get_db
from src.schemas.content import TagCreate, TagRead
from src.models.content import Tag, Content, content_tag_association
from src.models.viewing import Viewing

router = APIRouter(tags=["Tags"])

@router.get("")
async def get_tags(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort: str = "tag_id",
    order: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    
    query = (
        select(
            Tag.tag_id,
            Tag.tag_name,
            func.count(func.distinct(content_tag_association.c.content_id)).label("count"),
            func.count(Viewing.content_id).label("views_count")
        )
        .select_from(Tag)
        .outerjoin(content_tag_association, Tag.tag_id == content_tag_association.c.tag_id)
        .outerjoin(Viewing, content_tag_association.c.content_id == Viewing.content_id)
        .group_by(Tag.tag_id, Tag.tag_name)
    )
    
    count_query = select(func.count()).select_from(Tag)
    
    if search:
        query = query.where(Tag.tag_name.ilike(f"%{search}%"))
        count_query = count_query.where(Tag.tag_name.ilike(f"%{search}%"))
        
    if sort == "count":
        sort_column = func.count(func.distinct(content_tag_association.c.content_id))
    elif sort == "views_count":
        sort_column = func.count(Viewing.content_id)
    else:
        sort_column = getattr(Tag, sort, Tag.tag_id)
        
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
        
    result = await db.execute(query.limit(limit).offset(offset))
    rows = result.all()
    
    items = [
        {
            "tag_id": row[0],
            "tag_name": row[1],
            "count": row[2],
            "views_count": row[3]
        }
        for row in rows
    ]
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/popular")
async def get_popular_tags(
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Tag.tag_name, func.count().label("views_count"))
        .select_from(Tag)
        .join(content_tag_association, Tag.tag_id == content_tag_association.c.tag_id)
        .join(Viewing, content_tag_association.c.content_id == Viewing.content_id)
        .group_by(Tag.tag_name)
        .order_by(func.count().desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    return [{"tag_name": row[0], "views_count": row[1]} for row in result.all()]

@router.post("", response_model=TagRead)
async def create_tag(tag_data: TagCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tag).where(Tag.tag_name == tag_data.tag_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Exists")
    new_tag = Tag(tag_name=tag_data.tag_name)
    if tag_data.content_ids:
        content_res = await db.execute(select(Content).where(Content.content_id.in_(tag_data.content_ids)))
        new_tag.contents = list(content_res.scalars().all())
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag

@router.put("/{tag_id}", response_model=TagRead)
async def update_tag(tag_id: int, data: TagCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).options(selectinload(Tag.contents)).where(Tag.tag_id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Not found")
    tag.tag_name = data.tag_name
    if data.content_ids is not None:
        if data.content_ids:
            content_res = await db.execute(select(Content).where(Content.content_id.in_(data.content_ids)))
            tag.contents = list(content_res.scalars().all())
        else:
            tag.contents = []
    await db.commit()
    await db.refresh(tag)
    return tag

@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.tag_id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Not found")
    await db.execute(delete(Tag).where(Tag.tag_id == tag_id))
    await db.commit()
    return {"status": "success"}