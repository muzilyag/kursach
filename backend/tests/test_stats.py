import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_dashboard_statistics_admin(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/stats")
    assert response.status_code == 200
    assert "total_users" in response.json()
    assert "total_revenue" in response.json()

@pytest.mark.asyncio
async def test_get_dashboard_statistics_forbidden(auth_client_user: AsyncClient):
    response = await auth_client_user.get("/stats")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_dashboard_statistics_unauthorized(client: AsyncClient):
    response = await client.get("/stats")
    assert response.status_code == 401