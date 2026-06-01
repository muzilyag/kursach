import pytest
from httpx import AsyncClient
from src.models.user import User


@pytest.mark.asyncio
async def test_register_user_happy_path_returns_201(client: AsyncClient):
    payload = {
        "user_name": "newuser_happy",
        "user_email": "newuser_happy@example.com",
        "user_birth_date": "2000-01-01",
        "user_password": "securepassword",
        "user_role": "user",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["user_email"] == "newuser_happy@example.com"
    assert response.json()["user_name"] == "newuser_happy"


@pytest.mark.asyncio
async def test_register_with_forbidden_role_field_returns_422(client: AsyncClient):
    payload = {
        "user_name": "hacker_user",
        "user_email": "hacker@example.com",
        "user_birth_date": "1990-01-01",
        "user_password": "securepassword",
        "user_role": "superadmin",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_existing_user_email_returns_400(client: AsyncClient, normal_user: User):
    payload = {
        "user_name": "unique_username",
        "user_email": normal_user.user_email,
        "user_birth_date": "1995-01-01",
        "user_password": "userpass",
        "user_role": "user",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Пользователь с таким email или именем уже существует"


@pytest.mark.asyncio
async def test_register_existing_username_returns_400(client: AsyncClient, normal_user: User):
    payload = {
        "user_name": normal_user.user_name,
        "user_email": "unique_email@example.com",
        "user_birth_date": "1995-01-01",
        "user_password": "userpass",
        "user_role": "user",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Пользователь с таким email или именем уже существует"


@pytest.mark.asyncio
async def test_register_missing_required_fields_returns_422(client: AsyncClient):
    payload = {
        "user_name": "incomplete_user"
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success_with_email_returns_token(client: AsyncClient, normal_user: User):
    payload = {
        "identifier": normal_user.user_email,
        "password": "userpass"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_success_with_username_returns_token(client: AsyncClient, normal_user: User):
    payload = {
        "identifier": normal_user.user_name,
        "password": "userpass"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient, normal_user: User):
    payload = {
        "identifier": normal_user.user_email,
        "password": "wrongpassword"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"


@pytest.mark.asyncio
async def test_login_non_existent_user_returns_401(client: AsyncClient):
    payload = {
        "identifier": "ghost@nowhere.com",
        "password": "somepassword"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверное имя пользователя или пароль"


@pytest.mark.asyncio
async def test_login_missing_credentials_returns_422(client: AsyncClient):
    payload = {
        "identifier": "only_identifier"
    }
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 422