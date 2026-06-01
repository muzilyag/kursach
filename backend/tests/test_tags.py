import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.content import Tag, Content


@pytest.mark.asyncio
async def test_get_tags_unauthorized_returns_401(client: AsyncClient):
    response = await client.get("/tags")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_tags_forbidden_for_user_returns_403(auth_client_user: AsyncClient):
    response = await auth_client_user.get("/tags")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_tags_list_filters_success(
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
async def test_get_popular_tags_success(auth_client_content_manager: AsyncClient):
    response = await auth_client_content_manager.get("/tags/popular?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_popular_tags_limit_exceeded_returns_422(
    auth_client_content_manager: AsyncClient,
):
    response = await auth_client_content_manager.get("/tags/popular?limit=999")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_missing_name_returns_422(
    auth_client_content_manager: AsyncClient,
):
    payload = {"content_ids": []}
    response = await auth_client_content_manager.post("/tags", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_with_content_success(
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
async def test_create_tag_duplicate_returns_400(auth_client_content_manager: AsyncClient):
    payload = {"tag_name": "DuplicateTag", "content_ids": []}
    await auth_client_content_manager.post("/tags", json=payload)

    response = await auth_client_content_manager.post("/tags", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_tag_with_content_success(
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
    assert response.json()["tag_name"] == "Sci-Fi Updated"


@pytest.mark.asyncio
async def test_update_tag_clear_contents_success(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="Drama")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    payload_empty = {"tag_name": "Drama Empty", "content_ids": []}
    response = await auth_client_content_manager.put(
        f"/tags/{tag.tag_id}", json=payload_empty
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_tag_not_found_returns_404(auth_client_content_manager: AsyncClient):
    payload = {"tag_name": "NonExistent", "content_ids": []}
    response = await auth_client_content_manager.put("/tags/99999", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tag_success(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="ToDelete")
    db_session.add(tag)
    await db_session.commit()

    response = await auth_client_content_manager.delete(f"/tags/{tag.tag_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_delete_tag_not_found_returns_404(auth_client_content_manager: AsyncClient):
    response = await auth_client_content_manager.delete("/tags/99999")
    assert response.status_code == 404