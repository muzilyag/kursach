from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, desc, asc, func, not_
from src.models.user import User
from typing import List, Optional
import uuid


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        search: str = "",
        sort_by: str = "user_id",
        order: str = "asc",
        roles: Optional[List[str]] = None,
    ):
        offset = (page - 1) * limit
        query = select(User).where(not_(User.user_email.endswith("@deleted.local")))

        if search:
            query = query.where(
                or_(
                    User.user_name.ilike(f"%{search}%"),
                    User.user_email.ilike(f"%{search}%"),
                )
            )

        if roles:
            query = query.where(User.user_role.in_(roles))

        sort_column = getattr(User, sort_by, User.user_id)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_count(self, search: str = "", roles: Optional[List[str]] = None):
        query = select(func.count()).select_from(User).where(not_(User.user_email.endswith("@deleted.local")))
        if search:
            query = query.where(
                or_(
                    User.user_name.ilike(f"%{search}%"),
                    User.user_email.ilike(f"%{search}%"),
                )
            )

        if roles:
            query = query.where(User.user_role.in_(roles))

        result = await self.session.execute(query)
        return result.scalar()

    async def get_by_id(self, user_id: int):
        result = await self.session.execute(
            select(User).where(User.user_id == user_id, not_(User.user_email.endswith("@deleted.local")))
        )
        return result.scalar_one_or_none()

    async def create(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: int, update_data: dict):
        user = await self.get_by_id(user_id)
        if not user:
            return None
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int):
        user = await self.session.get(User, user_id)
        if not user:
            return False
            
        unique_hash = uuid.uuid4().hex 
        user.user_name = f"user_{unique_hash[:10]}"
        user.user_email = f"{unique_hash}@deleted.local"
        user.user_password = "deleted_account_invalid_hash"
        
        await self.session.commit()
        return True