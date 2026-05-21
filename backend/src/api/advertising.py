from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc
from typing import Optional
from datetime import date

from src.core.database import get_db
from src.models.advertising import Advertising
from src.schemas.advertising import AdvertisingCreate, AdvertisingUpdate, AdvertisingResponse, AdvertisingListResponse

router = APIRouter(tags=["Advertising"])

def _calculate_is_active(ad: Advertising) -> bool:
    current_date = date.today()
    return ad.advertising_start_date <= current_date <= ad.advertising_finish_date

@router.post("", response_model=AdvertisingResponse, status_code=201)
async def create_advertising(
    ad_in: AdvertisingCreate,
    db: AsyncSession = Depends(get_db)
):
    new_ad = Advertising(**ad_in.model_dump())
    db.add(new_ad)
    await db.commit()
    await db.refresh(new_ad)
    
    response_data = ad_in.model_dump()
    response_data["advertising_id"] = new_ad.advertising_id
    response_data["is_active"] = _calculate_is_active(new_ad)
    return response_data

@router.get("", response_model=AdvertisingListResponse)
async def get_advertisements(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    owner: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = "asc",
    db: AsyncSession = Depends(get_db)
):
    query = select(Advertising)
    
    if owner:
        query = query.where(Advertising.advertising_owner.ilike(f"%{owner}%"))
        
    total_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(total_query)
    
    sort_map = {
        "advertising_id": Advertising.advertising_id,
        "advertising_name": Advertising.advertising_name,
        "advertising_duration": Advertising.advertising_duration,
        "advertising_owner": Advertising.advertising_owner,
        "advertising_start_date": Advertising.advertising_start_date,
        "advertising_finish_date": Advertising.advertising_finish_date,
    }
    
    sort_attr = sort_map.get(sort, Advertising.advertising_id)
    
    if order == "desc":
        query = query.order_by(desc(sort_attr))
    else:
        query = query.order_by(asc(sort_attr))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    ads = result.scalars().all()
    
    items = []
    for ad in ads:
        ad_dict = {
            "advertising_id": ad.advertising_id,
            "advertising_name": ad.advertising_name,
            "advertising_duration": ad.advertising_duration,
            "advertising_owner": ad.advertising_owner,
            "advertising_start_date": ad.advertising_start_date,
            "advertising_finish_date": ad.advertising_finish_date,
            "is_active": _calculate_is_active(ad)
        }
        items.append(ad_dict)
    
    return AdvertisingListResponse(items=items, total=total)

@router.get("/{ad_id}", response_model=AdvertisingResponse)
async def get_advertising(
    ad_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Advertising).where(Advertising.advertising_id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertising not found")
        
    ad_dict = {
        "advertising_id": ad.advertising_id,
        "advertising_name": ad.advertising_name,
        "advertising_duration": ad.advertising_duration,
        "advertising_owner": ad.advertising_owner,
        "advertising_start_date": ad.advertising_start_date,
        "advertising_finish_date": ad.advertising_finish_date,
        "is_active": _calculate_is_active(ad)
    }
    return ad_dict

@router.put("/{ad_id}", response_model=AdvertisingResponse)
async def update_advertising(
    ad_id: int,
    ad_in: AdvertisingUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Advertising).where(Advertising.advertising_id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertising not found")
        
    update_data = ad_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ad, field, value)
        
    await db.commit()
    await db.refresh(ad)
    
    ad_dict = {
        "advertising_id": ad.advertising_id,
        "advertising_name": ad.advertising_name,
        "advertising_duration": ad.advertising_duration,
        "advertising_owner": ad.advertising_owner,
        "advertising_start_date": ad.advertising_start_date,
        "advertising_finish_date": ad.advertising_finish_date,
        "is_active": _calculate_is_active(ad)
    }
    return ad_dict

@router.delete("/{ad_id}", status_code=204)
async def delete_advertising(
    ad_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Advertising).where(Advertising.advertising_id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertising not found")
        
    await db.delete(ad)
    await db.commit()