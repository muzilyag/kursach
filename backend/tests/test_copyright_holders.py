import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.content import CopyrightHolder, Content


@pytest.mark.asyncio
async def test_get_copyright_holders_filters(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    holder = CopyrightHolder(
        copyright_holder_name="Filter Studio",
        copyright_holder_phone="+111",
        copyright_holder_email="filter@test.com",
    )
    db_session.add(holder)
    await db_session.commit()

    res_search = await auth_client_content_manager.get(
        "/copyright-holders", params={"search": "Filter"}
    )
    assert res_search.status_code == 200
    assert res_search.json()["total"] >= 1

    res_sort_count = await auth_client_content_manager.get(
        "/copyright-holders", params={"sort": "content_count", "order": "desc"}
    )
    assert res_sort_count.status_code == 200

    res_sort_id = await auth_client_content_manager.get(
        "/copyright-holders", params={"sort": "copyright_holder_id", "order": "asc"}
    )
    assert res_sort_id.status_code == 200


@pytest.mark.asyncio
async def test_create_copyright_holder_with_content(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    content = Content(
        content_name="StudioMovie",
        content_type="movie",
        content_duration=datetime.time(1, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add(content)
    await db_session.commit()
    await db_session.refresh(content)

    payload = {
        "copyright_holder_name": "Test Studio Content",
        "copyright_holder_phone": "+123456789",
        "copyright_holder_email": "studio@test.com",
        "content_ids": [content.content_id],
    }
    response = await auth_client_content_manager.post(
        "/copyright-holders", json=payload
    )
    assert response.status_code == 200
    assert response.json()["copyright_holder_name"] == "Test Studio Content"


@pytest.mark.asyncio
async def test_update_copyright_holder_with_content(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    holder = CopyrightHolder(
        copyright_holder_name="Update Studio",
        copyright_holder_phone="+111",
        copyright_holder_email="upd@test.com",
    )
    content = Content(
        content_name="UpdMovie",
        content_type="movie",
        content_duration=datetime.time(1, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )
    db_session.add_all([holder, content])
    await db_session.commit()
    await db_session.refresh(holder)
    await db_session.refresh(content)

    payload = {
        "copyright_holder_name": "Updated Studio Content",
        "copyright_holder_phone": "+222",
        "copyright_holder_email": "new@test.com",
        "content_ids": [content.content_id],
    }
    response = await auth_client_content_manager.put(
        f"/copyright-holders/{holder.copyright_holder_id}", json=payload
    )
    assert response.status_code == 200

    payload_empty = {
        "copyright_holder_name": "Updated Studio Empty",
        "copyright_holder_phone": "+333",
        "copyright_holder_email": "new@test.com",
        "content_ids": [],
    }
    res_empty = await auth_client_content_manager.put(
        f"/copyright-holders/{holder.copyright_holder_id}", json=payload_empty
    )
    assert res_empty.status_code == 200


@pytest.mark.asyncio
async def test_update_copyright_holder_not_found(
    auth_client_content_manager: AsyncClient,
):
    payload = {
        "copyright_holder_name": "Non Existent Studio",
        "copyright_holder_phone": "+000000000",
        "copyright_holder_email": "none@test.com",
        "content_ids": [],
    }
    response = await auth_client_content_manager.put(
        "/copyright-holders/99999", json=payload
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_copyright_holder(
    auth_client_content_manager: AsyncClient, db_session: AsyncSession
):
    holder = CopyrightHolder(
        copyright_holder_name="Delete Studio",
        copyright_holder_phone="+444",
        copyright_holder_email="del@test.com",
    )
    db_session.add(holder)
    await db_session.commit()

    response = await auth_client_content_manager.delete(
        f"/copyright-holders/{holder.copyright_holder_id}"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_copyright_holder_not_found(
    auth_client_content_manager: AsyncClient,
):
    response = await auth_client_content_manager.delete("/copyright-holders/99999")
    assert response.status_code == 404
