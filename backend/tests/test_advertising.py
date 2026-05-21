import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_advertising(client: AsyncClient):
    payload = {
        "advertising_name": "Test Ad",
        "advertising_duration": 30,
        "advertising_owner": "Test Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2025-12-31"
    }
    response = await client.post("/advertising", json=payload)
    assert response.status_code == 201
    assert response.json()["advertising_name"] == "Test Ad"
    assert "advertising_id" in response.json()
    assert "is_active" in response.json()

@pytest.mark.asyncio
async def test_get_advertisements(client: AsyncClient):
    payload = {
        "advertising_name": "List Ad",
        "advertising_duration": 15,
        "advertising_owner": "List Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2025-12-31"
    }
    await client.post("/advertising", json=payload)
    
    response = await client.get("/advertising")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1

@pytest.mark.asyncio
async def test_get_advertisements_by_owner(client: AsyncClient):
    payload = {
        "advertising_name": "Search Ad",
        "advertising_duration": 15,
        "advertising_owner": "UniqueOwner123",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2025-12-31"
    }
    await client.post("/advertising", json=payload)
    
    response = await client.get("/advertising", params={"owner": "UniqueOwner123"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["advertising_owner"] == "UniqueOwner123"

@pytest.mark.asyncio
async def test_get_advertising_by_id(client: AsyncClient):
    payload = {
        "advertising_name": "Single Ad",
        "advertising_duration": 60,
        "advertising_owner": "Single Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2025-12-31"
    }
    create_resp = await client.post("/advertising", json=payload)
    ad_id = create_resp.json()["advertising_id"]
    
    response = await client.get(f"/advertising/{ad_id}")
    assert response.status_code == 200
    assert response.json()["advertising_id"] == ad_id
    assert response.json()["advertising_name"] == "Single Ad"

@pytest.mark.asyncio
async def test_get_advertising_not_found(client: AsyncClient):
    response = await client.get("/advertising/999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_advertising(client: AsyncClient):
    payload = {
        "advertising_name": "Update Ad",
        "advertising_duration": 10,
        "advertising_owner": "Update Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2025-12-31"
    }
    create_resp = await client.post("/advertising", json=payload)
    ad_id = create_resp.json()["advertising_id"]
    
    update_payload = {
        "advertising_name": "Updated Ad Name",
        "advertising_duration": 20
    }
    response = await client.put(f"/advertising/{ad_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["advertising_name"] == "Updated Ad Name"
    assert response.json()["advertising_duration"] == '00:00:20'

@pytest.mark.asyncio
async def test_update_advertising_not_found(client: AsyncClient):
    update_payload = {"advertising_name": "Ghost Ad"}
    response = await client.put("/advertising/999999", json=update_payload)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_advertising(client: AsyncClient):
    payload = {
        "advertising_name": "Delete Ad",
        "advertising_duration": 5,
        "advertising_owner": "Delete Owner",
        "advertising_start_date": "2025-01-01",
        "advertising_finish_date": "2025-12-31"
    }
    create_resp = await client.post("/advertising", json=payload)
    ad_id = create_resp.json()["advertising_id"]
    
    delete_resp = await client.delete(f"/advertising/{ad_id}")
    assert delete_resp.status_code == 204
    
    get_resp = await client.get(f"/advertising/{ad_id}")
    assert get_resp.status_code == 404

@pytest.mark.asyncio
async def test_delete_advertising_not_found(client: AsyncClient):
    response = await client.delete("/advertising/999999")
    assert response.status_code == 404