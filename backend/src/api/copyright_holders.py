from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, delete, desc, asc
from src.core.database import get_db
from src.schemas.content import CopyrightHolderCreate, CopyrightHolderRead
from src.models.content import CopyrightHolder

router = APIRouter(tags=["Copyright Holders"])

@router.get("", response_model=List[CopyrightHolderRead])
async def get_copyright_holders(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort: str = "copyright_holder_id",
    order: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    query = select(CopyrightHolder)
    
    if search:
        query = query.where(CopyrightHolder.copyright_holder_name.ilike(f"%{search}%"))
    
    column = getattr(CopyrightHolder, sort, CopyrightHolder.copyright_holder_id)
    if order == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()

@router.post("", response_model=CopyrightHolderRead)
async def create_copyright_holder(data: CopyrightHolderCreate, db: AsyncSession = Depends(get_db)):
    new_holder = CopyrightHolder(**data.model_dump())
    db.add(new_holder)
    await db.commit()
    await db.refresh(new_holder)
    return new_holder

@router.put("/{holder_id}", response_model=CopyrightHolderRead)
async def update_copyright_holder(holder_id: int, data: CopyrightHolderCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CopyrightHolder).where(CopyrightHolder.copyright_holder_id == holder_id))
    holder = result.scalar_one_or_none()
    if not holder:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in data.model_dump().items():
        setattr(holder, key, value)
    await db.commit()
    await db.refresh(holder)
    return holder

@router.delete("/{holder_id}")
async def delete_copyright_holder(holder_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CopyrightHolder).where(CopyrightHolder.copyright_holder_id == holder_id))
    holder = result.scalar_one_or_none()
    if not holder:
        raise HTTPException(status_code=404, detail="Not found")
    await db.execute(delete(CopyrightHolder).where(CopyrightHolder.copyright_holder_id == holder_id))
    await db.commit()
    return {"status": "success"}