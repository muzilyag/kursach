import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.models.content import Tag


@pytest.mark.asyncio
async def test_create_advertising_unauthorized_returns_401(client: AsyncClient):
    payload = {
        "advertising_name": "Ghost Ad",
        "advertising_duration": "00:00:30",
        "advertising_owner": "Test Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    response = await client.post("/advertising", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_advertising_forbidden_for_user_returns_403(auth_client_user: AsyncClient):
    payload = {
        "advertising_name": "Forbidden Ad",
        "advertising_duration": "00:00:30",
        "advertising_owner": "Test Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    response = await auth_client_user.post("/advertising", json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_advertising_missing_fields_returns_422(
    auth_client_content_manager: AsyncClient
):
    payload = {
        "advertising_owner": "Test Owner",
    }
    response = await auth_client_content_manager.post("/advertising", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_advertising_success(auth_client_content_manager: AsyncClient):
    payload = {
        "advertising_name": "Test Ad",
        "advertising_duration": "00:00:30",
        "advertising_owner": "Test Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    response = await auth_client_content_manager.post("/advertising", json=payload)
    assert response.status_code == 201
    assert response.json()["advertising_name"] == "Test Ad"
    assert "advertising_id" in response.json()
    assert "is_active" in response.json()


@pytest.mark.asyncio
async def test_create_advertising_with_tags_success(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="PromoTag")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    payload = {
        "advertising_name": "Test Ad With Tags",
        "advertising_duration": "00:00:30",
        "advertising_owner": "Test Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
        "tag_ids": [tag.tag_id],
    }
    response = await auth_client_content_manager.post("/advertising", json=payload)
    assert response.status_code == 201

    ad_id = response.json()["advertising_id"]
    res = await db_session.execute(
        text("SELECT tag_id FROM suitable_for WHERE advetising_id = :a_id"),
        {"a_id": ad_id},
    )
    saved_tags = [row[0] for row in res.fetchall()]
    assert tag.tag_id in saved_tags


@pytest.mark.asyncio
async def test_get_advertisements_unauthorized_returns_401(client: AsyncClient):
    response = await client.get("/advertising")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_advertisements_complex_filters(
    auth_client_content_manager: AsyncClient,
):
    payload1 = {
        "advertising_name": "Ad A",
        "advertising_duration": "00:00:15",
        "advertising_owner": "Owner1",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    payload2 = {
        "advertising_name": "Ad B",
        "advertising_duration": "00:01:00",
        "advertising_owner": "Owner2",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    await auth_client_content_manager.post("/advertising", json=payload1)
    await auth_client_content_manager.post("/advertising", json=payload2)

    res_asc = await auth_client_content_manager.get(
        "/advertising",
        params={"sort": "advertising_duration", "order": "asc", "limit": 10},
    )
    assert res_asc.status_code == 200

    res_desc = await auth_client_content_manager.get(
        "/advertising", params={"sort": "advertising_name", "order": "desc"}
    )
    assert res_desc.status_code == 200

    res_owner = await auth_client_content_manager.get(
        "/advertising", params={"owner": "Owner2"}
    )
    assert res_owner.status_code == 200
    assert res_owner.json()["total"] >= 1
    assert res_owner.json()["items"][0]["advertising_owner"] == "Owner2"


@pytest.mark.asyncio
async def test_get_advertisements_show_expired(
    auth_client_content_manager: AsyncClient,
):
    payload_expired = {
        "advertising_name": "Expired Camp",
        "advertising_duration": "00:00:10",
        "advertising_owner": "ExpiredOwner",
        "advertising_start_date": "2020-01-01",
        "advertising_finish_date": "2021-01-01",
    }
    await auth_client_content_manager.post("/advertising", json=payload_expired)

    res_hide = await auth_client_content_manager.get(
        "/advertising", params={"owner": "ExpiredOwner", "show_expired": "false"}
    )
    assert res_hide.status_code == 200
    assert res_hide.json()["total"] == 0

    res_show = await auth_client_content_manager.get(
        "/advertising", params={"owner": "ExpiredOwner", "show_expired": "true"}
    )
    assert res_show.status_code == 200
    assert res_show.json()["total"] >= 1
    assert res_show.json()["items"][0]["advertising_name"] == "Expired Camp"


@pytest.mark.asyncio
async def test_get_advertising_by_id_success(auth_client_content_manager: AsyncClient):
    payload = {
        "advertising_name": "Single Ad",
        "advertising_duration": "00:01:00",
        "advertising_owner": "Single Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    create_resp = await auth_client_content_manager.post("/advertising", json=payload)
    ad_id = create_resp.json()["advertising_id"]

    response = await auth_client_content_manager.get(f"/advertising/{ad_id}")
    assert response.status_code == 200
    assert response.json()["advertising_id"] == ad_id


@pytest.mark.asyncio
async def test_get_advertising_not_found_returns_404(auth_client_content_manager: AsyncClient):
    response = await auth_client_content_manager.get("/advertising/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_advertising_success(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="UpdateTag")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    payload = {
        "advertising_name": "Update Ad",
        "advertising_duration": "00:00:10",
        "advertising_owner": "Update Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    create_resp = await auth_client_content_manager.post("/advertising", json=payload)
    ad_id = create_resp.json()["advertising_id"]

    update_payload = {
        "advertising_name": "Updated Ad Name",
        "advertising_duration": "00:00:20",
        "tag_ids": [tag.tag_id],
    }
    response = await auth_client_content_manager.put(
        f"/advertising/{ad_id}", json=update_payload
    )
    assert response.status_code == 200
    assert response.json()["advertising_name"] == "Updated Ad Name"

    res = await db_session.execute(
        text("SELECT tag_id FROM suitable_for WHERE advetising_id = :a_id"),
        {"a_id": ad_id},
    )
    saved_tags = [row[0] for row in res.fetchall()]
    assert tag.tag_id in saved_tags


@pytest.mark.asyncio
async def test_update_advertising_clear_tags_success(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    tag = Tag(tag_name="TempTag")
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    payload = {
        "advertising_name": "Clear Tag Ad",
        "advertising_duration": "00:00:10",
        "advertising_owner": "Clear Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
        "tag_ids": [tag.tag_id],
    }
    create_resp = await auth_client_content_manager.post("/advertising", json=payload)
    ad_id = create_resp.json()["advertising_id"]

    update_payload = {
        "advertising_name": "Clear Tag Ad Updated",
        "tag_ids": [],
    }
    response = await auth_client_content_manager.put(
        f"/advertising/{ad_id}", json=update_payload
    )
    assert response.status_code == 200

    res = await db_session.execute(
        text("SELECT tag_id FROM suitable_for WHERE advetising_id = :a_id"),
        {"a_id": ad_id},
    )
    saved_tags = res.fetchall()
    assert len(saved_tags) == 0


@pytest.mark.asyncio
async def test_update_advertising_not_found_returns_404(auth_client_content_manager: AsyncClient):
    update_payload = {"advertising_name": "Ghost Ad"}
    response = await auth_client_content_manager.put(
        "/advertising/999999", json=update_payload
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_advertising_success(auth_client_content_manager: AsyncClient):
    payload = {
        "advertising_name": "Delete Ad",
        "advertising_duration": "00:00:05",
        "advertising_owner": "Delete Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2030-12-31",
    }
    create_resp = await auth_client_content_manager.post("/advertising", json=payload)
    ad_id = create_resp.json()["advertising_id"]

    delete_resp = await auth_client_content_manager.delete(f"/advertising/{ad_id}")
    assert delete_resp.status_code == 204

    get_resp = await auth_client_content_manager.get(f"/advertising/{ad_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_advertising_not_found_returns_404(auth_client_content_manager: AsyncClient):
    response = await auth_client_content_manager.delete("/advertising/999999")
    assert response.status_code == 404