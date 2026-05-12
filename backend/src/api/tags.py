from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, delete, desc, asc
from src.core.database import get_db
from src.schemas.content import TagCreate, TagRead
from src.models.content import Tag

router = APIRouter(tags=["Tags"])

@router.get("", response_model=List[TagRead])
async def get_tags(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort: str = "tag_id",
    order: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    query = select(Tag)
    
    if search:
        query = query.where(Tag.tag_name.ilike(f"%{search}%"))
    
    column = getattr(Tag, sort, Tag.tag_id)
    if order == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))
        
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()

@router.post("", response_model=TagRead)
async def create_tag(tag_data: TagCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tag).where(Tag.tag_name == tag_data.tag_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Exists")
    new_tag = Tag(**tag_data.model_dump())
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag

@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).where(Tag.tag_id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Not found")
    await db.execute(delete(Tag).where(Tag.tag_id == tag_id))
    await db.commit()
    return {"status": "success"}