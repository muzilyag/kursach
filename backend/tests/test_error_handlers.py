import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_non_existent_route_returns_404(client: AsyncClient):
    response = await client.get("/some-non-existent-endpoint-abc")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_method_not_allowed_returns_405(client: AsyncClient):
    response = await client.post("/content/genres")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_malformed_json_returns_422(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        content="{broken_json: true,",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422