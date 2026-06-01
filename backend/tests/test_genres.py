import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.content import Genre


@pytest.mark.asyncio
async def test_get_genres_empty_database_returns_200_and_empty_list(client: AsyncClient):
    response = await client.get("/content/genres")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_genres_returns_added_data(client: AsyncClient, db_session: AsyncSession):
    genre = Genre(genre_name="Sci-Fi")
    db_session.add(genre)
    await db_session.commit()
    
    response = await client.get("/content/genres")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 1
    assert any(g["genre_name"] == "Sci-Fi" for g in data)