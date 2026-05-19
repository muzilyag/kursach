import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.content import Content

@pytest.mark.asyncio
async def test_create_content(auth_client_admin: AsyncClient):
    payload = {
        "content_name": "Inception",
        "content_type": "movie",
        "content_duration": "02:28:00",
        "content_publish_date": "2010-07-16",
        "content_discription": "A thief who steals corporate secrets",
        "genre_ids": [],
        "copyright_holder_ids": [],
        "tag_ids": []
    }
    response = await auth_client_admin.post("/content", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_get_content_list(client: AsyncClient, db_session: AsyncSession):
    content = Content(
        content_name="Interstellar",
        content_type="movie",
        content_duration=datetime.time(2, 49, 0),
        content_publish_date=datetime.date(2014, 11, 7),
        content_discription="A team of explorers travel through a wormhole"
    )
    db_session.add(content)
    await db_session.commit()
    response = await client.get("/content?page=1&limit=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 1

@pytest.mark.asyncio
async def test_update_content(auth_client_admin: AsyncClient, db_session: AsyncSession):
    content = Content(
        content_name="Old Movie Title",
        content_type="movie",
        content_duration=datetime.time(1, 30, 0),
        content_publish_date=datetime.date(2020, 1, 1),
        content_discription="Description"
    )
    db_session.add(content)
    await db_session.commit()
    payload = {
        "content_name": "New Movie Title",
        "content_type": "movie",
        "content_duration": "01:30:00",
        "content_publish_date": "2020-01-01",
        "content_discription": "Updated Description",
        "genre_ids": [],
        "copyright_holder_ids": [],
        "tag_ids": []
    }
    response = await auth_client_admin.put(f"/content/{content.content_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_update_viewing_progress(auth_client_user: AsyncClient, db_session: AsyncSession):
    content = Content(
        content_name="Test Progress Content",
        content_type="movie",
        content_duration=datetime.time(1, 45, 0),
        content_publish_date=datetime.date(2025, 1, 1),
        content_discription="Description"
    )
    db_session.add(content)
    await db_session.commit()
    payload = {"progress": 50}
    response = await auth_client_user.patch(f"/content/{content.content_id}/progress", json=payload)
    assert response.status_code == 200
    assert response.json()["current_progress"] == 50

@pytest.mark.asyncio
async def test_delete_content(auth_client_admin: AsyncClient, db_session: AsyncSession):
    content = Content(
        content_name="To Be Deleted",
        content_type="movie",
        content_duration=datetime.time(1, 0, 0),
        content_publish_date=datetime.date(2025, 1, 1),
        content_discription="Description"
    )
    db_session.add(content)
    await db_session.commit()
    response = await auth_client_admin.delete(f"/content/{content.content_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True