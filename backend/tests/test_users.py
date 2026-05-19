import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User

@pytest.mark.asyncio
async def test_get_users_as_admin(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/users")
    assert response.status_code == 200
    assert "users" in response.json()

@pytest.mark.asyncio
async def test_get_users_as_user(auth_client_user: AsyncClient):
    response = await auth_client_user.get("/users")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_user_as_admin(auth_client_admin: AsyncClient):
    payload = {
        "user_name": "created_by_admin",
        "user_email": "admin_created@test.com",
        "user_birth_date": "1990-05-05",
        "user_password": "password123",
        "user_role": "user"
    }
    response = await auth_client_admin.post("/users", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_update_user_as_admin(auth_client_admin: AsyncClient, normal_user):
    payload = {
        "user_name": "updated_name"
    }
    response = await auth_client_admin.put(f"/users/{normal_user.user_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_delete_user_as_admin(auth_client_admin: AsyncClient, normal_user):
    response = await auth_client_admin.delete(f"/users/{normal_user.user_id}")
    assert response.status_code == 200