import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_copyright_holders(client: AsyncClient):
    response = await client.get("/copyright-holders")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_copyright_holder(auth_client_admin: AsyncClient):
    payload = {
        "copyright_holder_name": "Test Studio",
        "copyright_holder_phone": "+123456789",
        "copyright_holder_email": "studio@test.com",
        "content_ids": []
    }
    response = await auth_client_admin.post("/copyright-holders", json=payload)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_copyright_holder_not_found(auth_client_admin: AsyncClient):
    payload = {
        "copyright_holder_name": "Non Existent Studio",
        "copyright_holder_phone": "+000000000",
        "copyright_holder_email": "none@test.com",
        "content_ids": []
    }
    response = await auth_client_admin.put("/copyright-holders/9999", json=payload)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_copyright_holder_not_found(auth_client_admin: AsyncClient):
    response = await auth_client_admin.delete("/copyright-holders/9999")
    assert response.status_code == 404