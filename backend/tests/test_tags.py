import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.content import Tag, Content


@pytest.mark.asyncio
async def test_get_tags_list_filters(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="TestFilterTag")
    db_session.add(tag)
    await db_session.commit()

    res_search = await auth_client_content_manager.get(
        "/tags", params={"search": "FilterTag"}
    )
    assert res_search.status_code == 200
    assert res_search.json()["total"] >= 1

    res_sort_count = await auth_client_content_manager.get(
        "/tags", params={"sort": "count", "order": "desc"}
    )
    assert res_sort_count.status_code == 200

    res_sort_views = await auth_client_content_manager.get(
        "/tags", params={"sort": "views_count", "order": "asc"}
    )
    assert res_sort_views.status_code == 200


@pytest.mark.asyncio
async def test_get_popular_tags(auth_client_content_manager: AsyncClient):
    response = await auth_client_content_manager.get("/tags/popular?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_tag_with_content(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    content = Content(
        content_name="TagMovie",
        content_type="movie",
        content_duration=datetime.time(1, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add(content)
    await db_session.commit()
    await db_session.refresh(content)

    payload = {"tag_name": "Action", "content_ids": [content.content_id]}
    response = await auth_client_content_manager.post("/tags", json=payload)
    assert response.status_code == 200
    assert response.json()["tag_name"] == "Action"


@pytest.mark.asyncio
async def test_create_tag_duplicate(auth_client_content_manager: AsyncClient):
    payload = {"tag_name": "DuplicateTag", "content_ids": []}
    await auth_client_content_manager.post("/tags", json=payload)

    response = await auth_client_content_manager.post("/tags", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_tag_with_content(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="Comedy")
    content = Content(
        content_name="ComedyMovie",
        content_type="movie",
        content_duration=datetime.time(1, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add_all([tag, content])
    await db_session.commit()
    await db_session.refresh(tag)
    await db_session.refresh(content)

    payload = {"tag_name": "Sci-Fi Updated", "content_ids": [content.content_id]}
    response = await auth_client_content_manager.put(
        f"/tags/{tag.tag_id}", json=payload
    )
    assert response.status_code == 200

    payload_empty = {"tag_name": "Sci-Fi Empty", "content_ids": []}
    res_empty = await auth_client_content_manager.put(
        f"/tags/{tag.tag_id}", json=payload_empty
    )
    assert res_empty.status_code == 200


@pytest.mark.asyncio
async def test_update_tag_not_found(auth_client_content_manager: AsyncClient):
    payload = {"tag_name": "NonExistent", "content_ids": []}
    response = await auth_client_content_manager.put("/tags/99999", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tag(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="ToDelete")
    db_session.add(tag)
    await db_session.commit()

    response = await auth_client_content_manager.delete(f"/tags/{tag.tag_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_tag_not_found(auth_client_content_manager: AsyncClient):
    response = await auth_client_content_manager.delete("/tags/99999")
    assert response.status_code == 404
