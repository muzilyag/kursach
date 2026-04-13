from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_
from src.core.database import get_db
from src.schemas.content import ContentCreate
from src.models.content import Content, Genre, CopyrightHolder

router = APIRouter()

@router.get("")
async def get_content(page: int = 1, limit: int = 10, search: str = "", sort: str = "content_id", order: str = "desc", db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    
    query = select(Content).options(
        selectinload(Content.genres),
        selectinload(Content.copyright_holders)
    )

    if search:
        query = query.where(
            or_(
                Content.content_name.ilike(f"%{search}%"),
                Content.content_discription.ilike(f"%{search}%"),
                Content.content_type.ilike(f"%{search}%")
            )
        )

    col = getattr(Content, sort, Content.content_id)
    if order == "desc":
        query = query.order_by(col.desc())
    else:
        query = query.order_by(col.asc())
    
    result = await db.execute(query.offset(offset).limit(limit))
    content_list = result.scalars().all()
    
    count_query = select(func.count()).select_from(Content)
    if search:
        count_query = count_query.where(
            or_(
                Content.content_name.ilike(f"%{search}%"),
                Content.content_discription.ilike(f"%{search}%"),
                Content.content_type.ilike(f"%{search}%")
            )
        )
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    formatted_result = []
    for c in content_list:
        genre_obj = c.genres[0] if c.genres else None
        holder_obj = c.copyright_holders[0] if c.copyright_holders else None
        
        formatted_result.append({
            "content_id": c.content_id,
            "Название": c.content_name,
            "Тип": c.content_type,
            "Длительность": str(c.content_duration),
            "Дата выпуска": str(c.content_publish_date) if c.content_publish_date else None,
            "Описание": c.content_discription,
            "Жанры": genre_obj.genre_name if genre_obj else "Не указан",
            "Правообладатели": holder_obj.copyright_holder_name if holder_obj else "Не указан",
            "genre_id": genre_obj.genre_id if genre_obj else "",
            "copyright_holder_id": holder_obj.copyright_holder_id if holder_obj else ""
        })
        
    return {
        "content": formatted_result,
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
    if data.genre_id:
        genre = await db.get(Genre, data.genre_id)
        if genre: new_content.genres = [genre]
    if data.copyright_holder_id:
        holder = await db.get(CopyrightHolder, data.copyright_holder_id)
        if holder: new_content.copyright_holders = [holder]
    db.add(new_content)
    await db.commit()
    return {"success": True, "id": new_content.content_id}

@router.put("/{content_id}")
async def update_content(content_id: int, data: ContentCreate, db: AsyncSession = Depends(get_db)):
    query = select(Content).options(selectinload(Content.genres), selectinload(Content.copyright_holders)).where(Content.content_id == content_id)
    result = await db.execute(query)
    content = result.scalar_one_or_none()
    if not content: raise HTTPException(status_code=404, detail="Контент не найден")
    content.content_name, content.content_type = data.content_name, data.content_type
    content.content_duration, content.content_publish_date = data.content_duration, data.content_publish_date
    content.content_discription = data.content_discription
    if data.genre_id:
        genre = await db.get(Genre, data.genre_id)
        content.genres = [genre] if genre else []
    else: content.genres = []
    if data.copyright_holder_id:
        holder = await db.get(CopyrightHolder, data.copyright_holder_id)
        content.copyright_holders = [holder] if holder else []
    else: content.copyright_holders = []
    await db.commit()
    return {"success": True, "message": "Контент обновлен"}

@router.delete("/{content_id}")
async def delete_content(content_id: int, db: AsyncSession = Depends(get_db)):
    content = await db.get(Content, content_id)
    if not content: raise HTTPException(status_code=404, detail="Контент не найден")
    await db.delete(content)
    await db.commit()
    return {"success": True, "message": "Контент удален"}

@router.get("/genres")
async def get_genres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Genre))
    genres = result.scalars().all()
    return [{"value": g.genre_id, "label": g.genre_name} for g in genres]

@router.get("/copyright-holders")
async def get_copyright_holders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CopyrightHolder))
    holders = result.scalars().all()
    return [{"value": h.copyright_holder_id, "label": h.copyright_holder_name} for h in holders]