import pytest
import pytest_asyncio
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.models.content import Content, Genre, Tag, CopyrightHolder
from src.models.advertising import Advertising


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def sample_content_relations(db_session: AsyncSession):
    genre = Genre(genre_name="Sci-Fi")
    tag = Tag(tag_name="Space")
    holder = CopyrightHolder(
        copyright_holder_name="Warner",
        copyright_holder_phone="123",
        copyright_holder_email="w@w.com",
    )
    db_session.add_all([genre, tag, holder])
    await db_session.flush()
    return {
        "genre_id": genre.genre_id,
        "tag_id": tag.tag_id,
        "holder_id": holder.copyright_holder_id,
    }


@pytest.mark.asyncio
async def test_create_content_with_relations(
    auth_client_content_manager: AsyncClient, sample_content_relations
):
    payload = {
        "content_name": "Interstellar",
        "content_type": "movie",
        "content_duration": "02:49:00",
        "content_publish_date": "2014-11-07",
        "content_discription": "Wormhole travel",
        "genre_ids": [sample_content_relations["genre_id"]],
        "tag_ids": [sample_content_relations["tag_id"]],
        "copyright_holder_ids": [sample_content_relations["holder_id"]],
    }
    response = await auth_client_content_manager.post("/content", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_create_content_no_relations(auth_client_content_manager: AsyncClient):
    payload = {
        "content_name": "Simple Video",
        "content_type": "video",
        "content_duration": "00:15:00",
        "content_publish_date": "2025-01-01",
        "content_discription": "No tags",
        "genre_ids": [],
        "tag_ids": [],
        "copyright_holder_ids": [],
    }
    response = await auth_client_content_manager.post("/content", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_get_content_filtered_complex(
    client: AsyncClient, db_session: AsyncSession, sample_content_relations
):
    genre = await db_session.get(Genre, sample_content_relations["genre_id"])
    tag = await db_session.get(Tag, sample_content_relations["tag_id"])
    holder = await db_session.get(
        CopyrightHolder, sample_content_relations["holder_id"]
    )

    content = Content(
        content_name="Test Complex Matrix",
        content_type="movie",
        content_duration=datetime.time(2, 10, 0),
        content_publish_date=datetime.date(1999, 3, 31),
        content_discription="Digital matrix world",
        genres=[genre] if genre else [],
        tags=[tag] if tag else [],
        copyright_holders=[holder] if holder else [],
    )

    db_session.add(content)
    await db_session.commit()

    params = {
        "search": "Matrix",
        "genre_ids": [sample_content_relations["genre_id"]],
        "tag_ids": [sample_content_relations["tag_id"]],
        "copyright_holder_ids": [sample_content_relations["holder_id"]],
        "page": 1,
        "limit": 10,
        "sort": "content_name",
        "order": "asc",
    }
    response = await client.get("/content", params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(c["content_name"] == "Test Complex Matrix" for c in data["items"])


@pytest.mark.asyncio
async def test_get_content_filtered_not_found(client: AsyncClient):
    params = {"genre_ids": [9999], "tag_ids": [9999]}
    response = await client.get("/content", params=params)
    assert response.status_code == 200
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_content_empty_pagination(client: AsyncClient):
    params = {"page": 999, "limit": 10}
    response = await client.get("/content", params=params)
    assert response.status_code == 200
    assert len(response.json()["items"]) == 0


@pytest.mark.asyncio
async def test_update_content_add_relations(
    auth_client_content_manager: AsyncClient,
    db_session: AsyncSession,
    sample_content_relations,
):
    content = Content(
        content_name="Blank Movie",
        content_type="movie",
        content_duration=datetime.time(1, 0, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add(content)
    await db_session.commit()

    payload = {
        "content_name": "Blank Movie Updated",
        "content_type": "movie",
        "content_duration": "01:30:00",
        "content_publish_date": "2025-01-01",
        "genre_ids": [sample_content_relations["genre_id"]],
        "tag_ids": [sample_content_relations["tag_id"]],
        "copyright_holder_ids": [sample_content_relations["holder_id"]],
    }
    response = await auth_client_content_manager.put(
        f"/content/{content.content_id}", json=payload
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_content_not_found(auth_client_content_manager: AsyncClient):
    payload = {
        "content_name": "Ghost",
        "content_type": "movie",
        "content_duration": "01:00:00",
        "content_publish_date": "2025-01-01",
    }
    response = await auth_client_content_manager.put("/content/99999", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_content_success(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    content = Content(
        content_name="To Delete",
        content_type="movie",
        content_duration=datetime.time(1, 0, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add(content)
    await db_session.commit()

    response = await auth_client_content_manager.delete(
        f"/content/{content.content_id}"
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_delete_content_not_found(auth_client_content_manager: AsyncClient):
    response = await auth_client_content_manager.delete("/content/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_viewing_progress_empty(
    auth_client_user: AsyncClient, db_session: AsyncSession
):
    content = Content(
        content_name="Unwatched",
        content_type="movie",
        content_duration=datetime.time(1, 0, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add(content)
    await db_session.commit()

    response = await auth_client_user.get(f"/content/{content.content_id}/progress")
    assert response.status_code == 200
    assert response.json()["progress"] == 0


@pytest.mark.asyncio
async def test_update_viewing_progress_new_and_existing(
    auth_client_user: AsyncClient, db_session: AsyncSession
):
    content = Content(
        content_name="To Watch Twice",
        content_type="movie",
        content_duration=datetime.time(1, 0, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add(content)
    await db_session.commit()

    payload1 = {"progress": 45}
    response1 = await auth_client_user.patch(
        f"/content/{content.content_id}/progress", json=payload1
    )
    assert response1.status_code == 200
    assert response1.json()["current_progress"] == 45

    payload2 = {"progress": 90}
    response2 = await auth_client_user.patch(
        f"/content/{content.content_id}/progress", json=payload2
    )
    assert response2.status_code == 200
    assert response2.json()["current_progress"] == 90


@pytest.mark.asyncio
async def test_update_viewing_progress_not_found(auth_client_user: AsyncClient):
    payload = {"progress": 50}
    response = await auth_client_user.patch("/content/99999/progress", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_content_advertising(client: AsyncClient, db_session: AsyncSession):
    tag = Tag(tag_name="AdTag")
    db_session.add(tag)
    await db_session.flush()

    content = Content(
        content_name="Ad Content",
        content_type="movie",
        content_duration=datetime.time(1, 0),
        content_publish_date=datetime.date(2025, 1, 1),
        tags=[tag],
    )
    db_session.add(content)
    await db_session.flush()

    ad = Advertising(
        advertising_name="Content Ad",
        advertising_duration=datetime.time(0, 0, 15),
        advertising_owner="Ad Owner",
        advertising_start_date=datetime.date.today() - datetime.timedelta(days=1),
        advertising_finish_date=datetime.date.today() + datetime.timedelta(days=1),
    )
    db_session.add(ad)
    await db_session.flush()

    await db_session.execute(
        text("INSERT INTO suitable_for (advetising_id, tag_id) VALUES (:a_id, :t_id)"),
        {"a_id": ad.advertising_id, "t_id": tag.tag_id},
    )
    await db_session.commit()

    response = await client.get(f"/content/{content.content_id}/advertising")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(a["advertising_name"] == "Content Ad" for a in data)


@pytest.mark.asyncio
async def test_get_content_advertising_not_found(client: AsyncClient):
    response = await client.get("/content/99999/advertising")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_genres(client: AsyncClient, sample_content_relations):
    response = await client.get("/content/genres")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_tags(client: AsyncClient, sample_content_relations):
    response = await client.get("/content/tags")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_copyright_holders(client: AsyncClient, sample_content_relations):
    response = await client.get("/content/copyright-holders")
    assert response.status_code == 200
    assert len(response.json()) > 0
