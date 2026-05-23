import pytest
from httpx import AsyncClient
from src.models.user import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    payload = {
        "user_name": "newuser",
        "user_email": "newuser@example.com",
        "user_birth_date": "2000-01-01",
        "user_password": "securepassword",
        "user_role": "user",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["user_email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_register_existing_user_email(client: AsyncClient, normal_user: User):
    payload = {
        "user_name": "different_name",
        "user_email": normal_user.user_email,
        "user_birth_date": "1995-01-01",
        "user_password": "userpass",
        "user_role": "user",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_existing_username(client: AsyncClient, normal_user: User):
    payload = {
        "user_name": normal_user.user_name,
        "user_email": "different@example.com",
        "user_birth_date": "1995-01-01",
        "user_password": "userpass",
        "user_role": "user",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success_email(client: AsyncClient, normal_user: User):
    payload = {"identifier": normal_user.user_email, "password": "userpass"}
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_success_username(client: AsyncClient, normal_user: User):
    payload = {"identifier": normal_user.user_name, "password": "userpass"}
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, normal_user: User):
    payload = {"identifier": normal_user.user_email, "password": "wrongpassword"}
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_non_existent_user(client: AsyncClient):
    payload = {"identifier": "ghost@nowhere.com", "password": "somepassword"}
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401
