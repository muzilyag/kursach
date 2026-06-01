import pytest
import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.models.subscription import Subscribe, SubscribeType


@pytest.mark.asyncio
async def test_get_users_unauthorized_returns_401(client: AsyncClient):
    response = await client.get("/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_users_forbidden_for_normal_user_returns_403(auth_client_user: AsyncClient):
    response = await auth_client_user.get("/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_users_as_admin_success(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/users?page=1&limit=10&search=test")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_users_filtered_by_role_and_sort_success(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get(
        "/users?page=1&limit=10&roles=admin&roles=superadmin&sort=user_name&order=desc"
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert all(u["user_role"] in ["admin", "superadmin"] for u in data["users"])


@pytest.mark.asyncio
async def test_get_me_unauthorized_returns_401(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_no_subscription_success(auth_client_user: AsyncClient):
    response = await auth_client_user.get("/users/me")
    assert response.status_code == 200
    assert response.json()["active_subscription"] is None


@pytest.mark.asyncio
async def test_get_me_with_subscription_success(
    auth_client_user: AsyncClient, normal_user: User, db_session: AsyncSession
):
    sub_type = SubscribeType(
        subscribe_type_name="Test Sub",
        subscribe_type_discription="Desc",
        subscribe_type_max_type_quality=4,
        subscribe_type_cost=100.0,
        subscribe_type_duration=30,
    )
    db_session.add(sub_type)
    await db_session.flush()

    sub = Subscribe(
        user_id=normal_user.user_id,
        subscribe_type_id=sub_type.subscribe_type_id,
        subscribe_start=datetime.date.today(),
        subscribe_finish=datetime.date.today() + datetime.timedelta(days=30),
    )
    db_session.add(sub)
    await db_session.flush()

    response = await auth_client_user.get("/users/me")
    assert response.status_code == 200
    assert response.json()["active_subscription"] is not None
    assert response.json()["active_subscription"]["status"] == "Активна"


@pytest.mark.asyncio
async def test_patch_me_user_ignores_role_change(auth_client_user: AsyncClient):
    payload = {"user_name": "new_name", "user_role": "admin"}
    response = await auth_client_user.patch("/users/me", json=payload)
    assert response.status_code == 200
    assert response.json()["user_name"] == "new_name"
    assert response.json()["user_role"] == "user"


@pytest.mark.asyncio
async def test_patch_me_password_success(auth_client_user: AsyncClient):
    payload = {"user_password": "new_patched_password"}
    response = await auth_client_user.patch("/users/me", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_patch_me_as_admin_ignores_superadmin_role(auth_client_admin: AsyncClient):
    payload = {"user_role": "superadmin"}
    response = await auth_client_admin.patch("/users/me", json=payload)
    assert response.status_code == 200
    assert response.json()["user_role"] == "admin"


@pytest.mark.asyncio
async def test_change_password_success(auth_client_user: AsyncClient):
    payload = {"old_password": "userpass", "new_password": "new_secure_password"}
    response = await auth_client_user.patch("/users/me/password", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_change_password_wrong_old_returns_400(auth_client_user: AsyncClient):
    payload = {"old_password": "wrong_password", "new_password": "new_secure_password"}
    response = await auth_client_user.patch("/users/me/password", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_password_missing_fields_returns_422(auth_client_user: AsyncClient):
    payload = {"new_password": "only_new_password"}
    response = await auth_client_user.patch("/users/me/password", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_me_success(auth_client_user: AsyncClient):
    response = await auth_client_user.delete("/users/me")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_get_user_by_id_success(auth_client_admin: AsyncClient, normal_user: User):
    response = await auth_client_admin.get(f"/users/{normal_user.user_id}")
    assert response.status_code == 200
    assert response.json()["user_email"] == normal_user.user_email


@pytest.mark.asyncio
async def test_get_user_by_id_not_found_returns_404(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/users/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user_admin_creating_admin_returns_403(auth_client_admin: AsyncClient):
    payload = {
        "user_name": "new_admin",
        "user_email": "new_admin@test.com",
        "user_birth_date": "1990-01-01",
        "user_password": "password123",
        "user_role": "admin",
    }
    response = await auth_client_admin.post("/users", json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_superadmin_creating_admin_success(
    auth_client_superadmin: AsyncClient,
):
    payload = {
        "user_name": "new_admin_by_super",
        "user_email": "admin_by_super@test.com",
        "user_birth_date": "1990-01-01",
        "user_password": "password123",
        "user_role": "admin",
    }
    response = await auth_client_superadmin.post("/users", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_user_success(auth_client_admin: AsyncClient):
    payload = {
        "user_name": "new_user_ok",
        "user_email": "ok@test.com",
        "user_birth_date": "1990-01-01",
        "user_password": "password123",
        "user_role": "user",
    }
    response = await auth_client_admin.post("/users", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_user_missing_fields_returns_422(auth_client_admin: AsyncClient):
    payload = {
        "user_name": "incomplete_user",
        "user_role": "user",
    }
    response = await auth_client_admin.post("/users", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_duplicate_email_returns_400(
    auth_client_admin: AsyncClient, normal_user: User, db_session: AsyncSession
):
    payload = {
        "user_name": "copycat",
        "user_email": normal_user.user_email,
        "user_birth_date": "1990-01-01",
        "user_password": "password123",
        "user_role": "user",
    }
    await db_session.begin_nested()
    response = await auth_client_admin.post("/users", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_user_success(auth_client_admin: AsyncClient, normal_user: User):
    payload = {"user_name": "updated_by_admin", "user_password": "new_password"}
    response = await auth_client_admin.put(
        f"/users/{normal_user.user_id}", json=payload
    )
    assert response.status_code == 200
    assert response.json()["user"]["user_name"] == "updated_by_admin"


@pytest.mark.asyncio
async def test_update_user_duplicate_email_returns_400(
    auth_client_admin: AsyncClient,
    normal_user: User,
    admin_user: User,
    db_session: AsyncSession,
):
    payload = {"user_email": admin_user.user_email}
    await db_session.begin_nested()
    response = await auth_client_admin.put(
        f"/users/{normal_user.user_id}", json=payload
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_user_not_found_returns_404(auth_client_admin: AsyncClient):
    payload = {"user_name": "ghost"}
    response = await auth_client_admin.put("/users/99999", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_success(
    auth_client_admin: AsyncClient, db_session: AsyncSession
):
    user = User(
        user_name="to_delete",
        user_email="delete@example.com",
        user_birth_date=datetime.date(2000, 1, 1),
        user_password="password",
        user_role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await auth_client_admin.delete(f"/users/{user.user_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_delete_user_not_found_returns_404(auth_client_admin: AsyncClient):
    response = await auth_client_admin.delete("/users/99999")
    assert response.status_code == 404