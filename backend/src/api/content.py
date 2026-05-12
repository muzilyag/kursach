from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_
from src.core.database import get_db
from src.schemas.content import ContentCreate
from src.models.content import Content, Genre, CopyrightHolder, Tag

router = APIRouter()

@router.get("")
async def get_content(
    page: int = 1, 
    limit: int = 10, 
    search: str = "", 
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
        query = query.where(
            or_(
                Content.content_name.ilike(f"%{search}%"),
                Content.content_description.ilike(f"%{search}%")
            )
        )

    col = getattr(Content, sort, Content.content_id)
    query = query.order_by(col.desc() if order == "desc" else col.asc())
    
    result = await db.execute(query.offset(offset).limit(limit))
    content_list = result.scalars().all()
    
    count_query = select(func.count()).select_from(Content)
    if search:
        count_query = count_query.where(
            or_(
                Content.content_name.ilike(f"%{search}%"),
                Content.content_description.ilike(f"%{search}%")
            )
        )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    formatted_result = []
    for c in content_list:
        formatted_result.append({
            "content_id": c.content_id,
            "content_name": c.content_name,
            "content_type": c.content_type,
            "content_duration": str(c.content_duration),
            "content_publish_date": str(c.content_publish_date) if c.content_publish_date else None,
            "content_description": c.content_description,
            "genres": [
                {"genre_id": g.genre_id, "genre_name": g.genre_name} 
                for g in c.genres
            ],
            "tags": [
                {"tag_id": t.tag_id, "tag_name": t.tag_name} 
                for t in c.tags
            ],
            "copyright_holders": [
                {
                    "copyright_holder_id": h.copyright_holder_id, 
                    "copyright_holder_name": h.copyright_holder_name
                } 
                for h in c.copyright_holders
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
        content_description=data.content_description
    )
    
    if data.genre_ids:
        genres_result = await db.execute(select(Genre).where(Genre.genre_id.in_(data.genre_ids)))
        new_content.genres = list(genres_result.scalars().all())
        
    if data.copyright_holder_ids:
        holders_result = await db.execute(select(CopyrightHolder).where(CopyrightHolder.copyright_holder_id.in_(data.copyright_holder_ids)))
        new_content.copyright_holders = list(holders_result.scalars().all())
        
    if data.tag_ids:
        tags_result = await db.execute(select(Tag).where(Tag.tag_id.in_(data.tag_ids)))
        new_content.tags = list(tags_result.scalars().all())
        
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
    content.content_description = data.content_description
    
    if data.genre_ids:
        genres_result = await db.execute(select(Genre).where(Genre.genre_id.in_(data.genre_ids)))
        content.genres = list(genres_result.scalars().all())
    else: 
        content.genres = []
        
    if data.copyright_holder_ids:
        holders_result = await db.execute(select(CopyrightHolder).where(CopyrightHolder.copyright_holder_id.in_(data.copyright_holder_ids)))
        content.copyright_holders = list(holders_result.scalars().all())
    else: 
        content.copyright_holders = []

    if data.tag_ids:
        tags_result = await db.execute(select(Tag).where(Tag.tag_id.in_(data.tag_ids)))
        content.tags = list(tags_result.scalars().all())
    else: 
        content.tags = []
        
    await db.commit()
    return {"success": True, "message": "Контент обновлен"}

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