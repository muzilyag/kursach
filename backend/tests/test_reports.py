import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_activity_report(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/reports/activity")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_activity_report_export_csv(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/reports/activity?export=true&format=csv")
    assert response.status_code == 404 

@pytest.mark.asyncio
async def test_get_revenue_report(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/reports/revenue?start_date=2026-01-01&end_date=2026-12-31")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_revenue_report_missing_params(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/reports/revenue")
    assert response.status_code == 422