import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_not_found_route(client: AsyncClient):
    response = await client.get("/some-non-existent-endpoint-abc")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_method_not_allowed(client: AsyncClient):
    response = await client.post("/content/genres")
    assert response.status_code == 405
