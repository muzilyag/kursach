from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc, asc, func
from src.core.database import get_db
from src.schemas.content import CopyrightHolderCreate, CopyrightHolderRead
from src.models.content import CopyrightHolder, Content, content_copyright_association
from src.core.security import RoleChecker

router = APIRouter(tags=["Copyright Holders"])


@router.get("", dependencies=[Depends(RoleChecker(["content_manager", "superadmin"]))])
async def get_copyright_holders(
    search: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort: str = "copyright_holder_id",
    order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit

    query = (
        select(
            CopyrightHolder.copyright_holder_id,
            CopyrightHolder.copyright_holder_name,
            CopyrightHolder.copyright_holder_phone,
            CopyrightHolder.copyright_holder_email,
            func.count(content_copyright_association.c.content_id).label(
                "content_count"
            ),
        )
        .select_from(CopyrightHolder)
        .outerjoin(
            content_copyright_association,
            CopyrightHolder.copyright_holder_id
            == content_copyright_association.c.copyright_holder_id,
        )
        .group_by(
            CopyrightHolder.copyright_holder_id,
            CopyrightHolder.copyright_holder_name,
            CopyrightHolder.copyright_holder_phone,
            CopyrightHolder.copyright_holder_email,
        )
    )

    count_query = select(func.count()).select_from(CopyrightHolder)

    if search:
        query = query.where(CopyrightHolder.copyright_holder_name.ilike(f"%{search}%"))
        count_query = count_query.where(
            CopyrightHolder.copyright_holder_name.ilike(f"%{search}%")
        )

    if sort == "content_count":
        sort_column = func.count(content_copyright_association.c.content_id)
    else:
        sort_column = getattr(
            CopyrightHolder, sort, CopyrightHolder.copyright_holder_id
        )

    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    result = await db.execute(query.limit(limit).offset(offset))
    rows = result.all()

    items = [
        {
            "copyright_holder_id": row[0],
            "copyright_holder_name": row[1],
            "copyright_holder_phone": row[2],
            "copyright_holder_email": row[3],
            "content_count": row[4],
        }
        for row in rows
    ]

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.post(
    "",
    response_model=CopyrightHolderRead,
    dependencies=[Depends(RoleChecker(["content_manager", "superadmin"]))],
)
async def create_copyright_holder(
    data: CopyrightHolderCreate, db: AsyncSession = Depends(get_db)
):
    holder_dict = data.model_dump(exclude={"content_ids"})

    contents_list = []
    if data.content_ids:
        c_res = await db.execute(
            select(Content).where(Content.content_id.in_(data.content_ids))
        )
        contents_list = list(c_res.scalars().all())

    new_holder = CopyrightHolder(**holder_dict, contents=contents_list)

    db.add(new_holder)
    await db.commit()

    final_res = await db.execute(
        select(CopyrightHolder)
        .options(selectinload(CopyrightHolder.contents))
        .where(CopyrightHolder.copyright_holder_id == new_holder.copyright_holder_id)
    )
    return final_res.scalar_one()


@router.put(
    "/{holder_id}",
    response_model=CopyrightHolderRead,
    dependencies=[Depends(RoleChecker(["content_manager", "superadmin"]))],
)
async def update_copyright_holder(
    holder_id: int, data: CopyrightHolderCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CopyrightHolder)
        .options(selectinload(CopyrightHolder.contents))
        .where(CopyrightHolder.copyright_holder_id == holder_id)
    )
    holder = result.scalar_one_or_none()
    if not holder:
        raise HTTPException(status_code=404, detail="Not found")

    for key, value in data.model_dump(exclude={"content_ids"}).items():
        setattr(holder, key, value)

    if data.content_ids is not None:
        if data.content_ids:
            c_res = await db.execute(
                select(Content).where(Content.content_id.in_(data.content_ids))
            )
            holder.contents = list(c_res.scalars().all())
        else:
            holder.contents = []

    await db.commit()

    final_res = await db.execute(
        select(CopyrightHolder)
        .options(selectinload(CopyrightHolder.contents))
        .where(CopyrightHolder.copyright_holder_id == holder_id)
    )
    return final_res.scalar_one()


@router.delete(
    "/{holder_id}",
    dependencies=[Depends(RoleChecker(["content_manager", "superadmin"]))],
)
async def delete_copyright_holder(holder_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CopyrightHolder)
        .options(selectinload(CopyrightHolder.contents))
        .where(CopyrightHolder.copyright_holder_id == holder_id)
    )
    holder = result.scalar_one_or_none()
    if not holder:
        raise HTTPException(status_code=404, detail="Not found")

    holder.contents = []
    await db.commit()

    await db.delete(holder)
    await db.commit()
    return {"status": "success"}
