import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    payload = {
        "user_name": "newuser",
        "user_email": "newuser@example.com",
        "user_birth_date": "2000-01-01",
        "user_password": "securepassword",
        "user_role": "user"
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["user_email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_register_existing_user(client: AsyncClient, normal_user):
    payload = {
        "user_name": "normal_test",
        "user_email": "user@test.com",
        "user_birth_date": "1995-01-01",
        "user_password": "userpass",
        "user_role": "user"
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, normal_user):
    payload = {
        "identifier": "user@test.com",
        "password": "userpass"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, normal_user):
    payload = {
        "identifier": "user@test.com",
        "password": "wrongpassword"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_non_existent_user(client: AsyncClient):
    payload = {
        "identifier": "nobody@test.com",
        "password": "password"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401