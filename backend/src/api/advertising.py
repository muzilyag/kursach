from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc, text
from typing import Optional
from datetime import date
from src.models.user import UserRole

from src.core.database import get_db
from src.models.advertising import Advertising
from src.schemas.advertising import (
    AdvertisingCreate,
    AdvertisingUpdate,
    AdvertisingResponse,
    AdvertisingListResponse,
)
from src.core.security import RoleChecker

router = APIRouter(tags=["Advertising"])


def _calculate_is_active(ad: Advertising) -> bool:
    current_date = date.today()
    return ad.advertising_start_date <= current_date <= ad.advertising_finish_date


@router.post(
    "",
    response_model=AdvertisingResponse,
    status_code=201,
    dependencies=[Depends(RoleChecker([UserRole.content_manager.value, UserRole.superadmin.value]))],
)
async def create_advertising(
    ad_in: AdvertisingCreate, db: AsyncSession = Depends(get_db)
):
    ad_data = ad_in.model_dump(exclude={"tag_ids"})
    new_ad = Advertising(**ad_data)
    db.add(new_ad)
    await db.commit()
    await db.refresh(new_ad)

    if ad_in.tag_ids:
        for t_id in ad_in.tag_ids:
            await db.execute(
                text(
                    "INSERT INTO suitable_for (advetising_id, tag_id) VALUES (:a_id, :t_id)"
                ),
                {"a_id": new_ad.advertising_id, "t_id": t_id},
            )
        await db.commit()

    response_data = ad_in.model_dump(exclude={"tag_ids"})
    response_data["advertising_id"] = new_ad.advertising_id
    response_data["is_active"] = _calculate_is_active(new_ad)
    return response_data


@router.get(
    "",
    response_model=AdvertisingListResponse,
    dependencies=[Depends(RoleChecker([UserRole.content_manager.value, UserRole.superadmin.value]))],
)
async def get_advertisements(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    owner: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = "asc",
    show_expired: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    query = select(Advertising)

    if owner:
        query = query.where(Advertising.advertising_owner.ilike(f"%{owner}%"))

    if not show_expired:
        query = query.where(Advertising.advertising_finish_date >= date.today())

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
            "is_active": _calculate_is_active(ad),
        }
        items.append(ad_dict)

    return AdvertisingListResponse(items=items, total=total)


@router.get("/{ad_id}", response_model=AdvertisingResponse)
async def get_advertising(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Advertising).where(Advertising.advertising_id == ad_id)
    )
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
        "is_active": _calculate_is_active(ad),
    }
    return ad_dict


@router.put(
    "/{ad_id}",
    response_model=AdvertisingResponse,
    dependencies=[Depends(RoleChecker([UserRole.content_manager.value, UserRole.superadmin.value]))],
)
async def update_advertising(
    ad_id: int, ad_in: AdvertisingUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Advertising).where(Advertising.advertising_id == ad_id)
    )
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertising not found")

    update_data = ad_in.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for field, value in update_data.items():
        setattr(ad, field, value)

    await db.commit()
    await db.refresh(ad)

    if ad_in.tag_ids is not None:
        await db.execute(
            text("DELETE FROM suitable_for WHERE advetising_id = :a_id"),
            {"a_id": ad_id},
        )
        if ad_in.tag_ids:
            for t_id in ad_in.tag_ids:
                await db.execute(
                    text(
                        "INSERT INTO suitable_for (advetising_id, tag_id) VALUES (:a_id, :t_id)"
                    ),
                    {"a_id": ad_id, "t_id": t_id},
                )
        await db.commit()

    ad_dict = {
        "advertising_id": ad.advertising_id,
        "advertising_name": ad.advertising_name,
        "advertising_duration": ad.advertising_duration,
        "advertising_owner": ad.advertising_owner,
        "advertising_start_date": ad.advertising_start_date,
        "advertising_finish_date": ad.advertising_finish_date,
        "is_active": _calculate_is_active(ad),
    }
    return ad_dict


@router.delete(
    "/{ad_id}",
    status_code=204,
    dependencies=[Depends(RoleChecker([UserRole.content_manager.value, UserRole.superadmin.value]))],
)
async def delete_advertising(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Advertising).where(Advertising.advertising_id == ad_id)
    )
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Advertising not found")

    await db.delete(ad)
    await db.commit()
