from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from src.models.content import Content, Genre, CopyrightHolder


class ContentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_content(self, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        query = (
            select(Content)
            .options(
                selectinload(Content.genres), selectinload(Content.copyright_holders)
            )
            .order_by(Content.content_name)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_content_count(self):
        query = select(func.count()).select_from(Content)
        result = await self.session.execute(query)
        return result.scalar()

    async def create_content(
        self, content_data: dict, genre_id: int, copyright_holder_id: int
    ):
        new_content = Content(
            content_name=content_data.get("content_name"),
            content_type=content_data.get("content_type"),
            content_duration=content_data.get("content_duration"),
            content_publish_date=content_data.get("content_publish_date"),
            content_discription=content_data.get("content_discription"),
        )

        genre = await self.session.get(Genre, genre_id)
        if genre:
            new_content.genres.append(genre)

        holder = await self.session.get(CopyrightHolder, copyright_holder_id)
        if holder:
            new_content.copyright_holders.append(holder)

        self.session.add(new_content)
        await self.session.commit()
        await self.session.refresh(new_content)
        return new_content

    async def get_genres(self):
        query = select(Genre).order_by(Genre.genre_name)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_copyright_holders(self):
        query = select(CopyrightHolder).order_by(CopyrightHolder.copyright_holder_name)
        result = await self.session.execute(query)
        return result.scalars().all()
