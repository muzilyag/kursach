import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.content import Tag

@pytest.mark.asyncio
async def test_get_tags_list(client: AsyncClient):
    response = await client.get("/tags")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_tag(auth_client_admin: AsyncClient):
    payload = {
        "tag_name": "Action",
        "content_ids": []
    }
    response = await auth_client_admin.post("/tags", json=payload)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_tag(auth_client_admin: AsyncClient, db_session: AsyncSession):
    tag = Tag(tag_name="Comedy")
    db_session.add(tag)
    await db_session.commit()
    payload = {
        "tag_name": "Sci-Fi",
        "content_ids": []
    }
    response = await auth_client_admin.put(f"/tags/{tag.tag_id}", json=payload)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_tag_not_found(auth_client_admin: AsyncClient):
    payload = {
        "tag_name": "NonExistent",
        "content_ids": []
    }
    response = await auth_client_admin.put("/tags/9999", json=payload)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_tag_not_found(auth_client_admin: AsyncClient):
    response = await auth_client_admin.delete("/tags/9999")
    assert response.status_code == 404