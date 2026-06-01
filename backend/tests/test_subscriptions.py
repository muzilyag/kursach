import pytest
import pytest_asyncio
import datetime
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.subscription import SubscribeType, Subscribe
from src.models.user import User


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def sample_sub_type(db_session: AsyncSession):
    sub_type = SubscribeType(
        subscribe_type_name="Premium",
        subscribe_type_discription="All access",
        subscribe_type_max_type_quality=4,
        subscribe_type_cost=Decimal("299.00"),
        subscribe_type_duration=30,
    )
    db_session.add(sub_type)
    await db_session.flush()
    return sub_type


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def another_sub_type(db_session: AsyncSession):
    sub_type = SubscribeType(
        subscribe_type_name="Basic",
        subscribe_type_discription="Basic access",
        subscribe_type_max_type_quality=2,
        subscribe_type_cost=Decimal("199.00"),
        subscribe_type_duration=30,
    )
    db_session.add(sub_type)
    await db_session.flush()
    return sub_type


@pytest.mark.asyncio
async def test_get_subscription_types_unauthorized_returns_401(client: AsyncClient):
    response = await client.get("/subscriptions/types")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_subscription_types_success(auth_client_user: AsyncClient, sample_sub_type):
    response = await auth_client_user.get("/subscriptions/types")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_buy_subscription_missing_payload_returns_422(auth_client_user: AsyncClient):
    response = await auth_client_user.post("/subscriptions/buy", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_buy_subscription_admin_forbidden_returns_403(
    auth_client_admin: AsyncClient, sample_sub_type
):
    payload = {
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    response = await auth_client_admin.post("/subscriptions/buy", json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_buy_subscription_success(auth_client_user: AsyncClient, sample_sub_type):
    payload = {
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    response = await auth_client_user.post("/subscriptions/buy", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_buy_subscription_existing_same_type_extends(
    auth_client_user: AsyncClient, sample_sub_type
):
    payload = {
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    await auth_client_user.post("/subscriptions/buy", json=payload)
    response = await auth_client_user.post("/subscriptions/buy", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_buy_subscription_existing_different_type_returns_400(
    auth_client_user: AsyncClient, sample_sub_type, another_sub_type
):
    payload1 = {
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    await auth_client_user.post("/subscriptions/buy", json=payload1)

    payload2 = {
        "subscribe_type_id": another_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    response = await auth_client_user.post("/subscriptions/buy", json=payload2)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_buy_subscription_type_not_found_returns_404(auth_client_user: AsyncClient):
    payload = {"subscribe_type_id": 999999, "payment_method": "карта"}
    response = await auth_client_user.post("/subscriptions/buy", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_preview_subscription_change_no_active(
    auth_client_user: AsyncClient, sample_sub_type
):
    response = await auth_client_user.get(
        f"/subscriptions/preview-change?target_type_id={sample_sub_type.subscribe_type_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_tariff_id"] is None
    assert data["target_tariff_id"] == sample_sub_type.subscribe_type_id


@pytest.mark.asyncio
async def test_preview_subscription_change_same_active(
    auth_client_user: AsyncClient, sample_sub_type
):
    payload = {
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    await auth_client_user.post("/subscriptions/buy", json=payload)

    response = await auth_client_user.get(
        f"/subscriptions/preview-change?target_type_id={sample_sub_type.subscribe_type_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_tariff_id"] == sample_sub_type.subscribe_type_id
    assert data["discount_amount"] == "0.00"


@pytest.mark.asyncio
async def test_preview_subscription_change_different_active(
    auth_client_user: AsyncClient, sample_sub_type, another_sub_type
):
    payload = {
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    await auth_client_user.post("/subscriptions/buy", json=payload)

    response = await auth_client_user.get(
        f"/subscriptions/preview-change?target_type_id={another_sub_type.subscribe_type_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_tariff_id"] == sample_sub_type.subscribe_type_id
    assert float(data["discount_amount"]) > 0.0


@pytest.mark.asyncio
async def test_preview_subscription_change_target_not_found_returns_404(
    auth_client_user: AsyncClient,
):
    response = await auth_client_user.get("/subscriptions/preview-change?target_type_id=999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_users_filtered_active(
    auth_client_admin: AsyncClient,
    sample_sub_type,
    db_session: AsyncSession,
    normal_user: User,
):
    sub = Subscribe(
        user_id=normal_user.user_id,
        subscribe_type_id=sample_sub_type.subscribe_type_id,
        subscribe_start=datetime.date.today() - datetime.timedelta(days=5),
        subscribe_finish=datetime.date.today() + datetime.timedelta(days=25),
    )
    db_session.add(sub)
    await db_session.flush()
    response = await auth_client_admin.get("/subscriptions/users-filtered?has_active=true")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_users_filtered_inactive(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/subscriptions/users-filtered?has_active=false")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_subscriptions_list_with_complex_filters(auth_client_admin: AsyncClient):
    params = {
        "search": "test",
        "sort": "subscribe_type_name",
        "order": "asc",
        "show_expired": "true",
        "start_date": "2020-01-01",
        "end_date": "2030-01-01",
        "page": 1,
        "limit": 5,
    }
    response = await auth_client_admin.get("/subscriptions", params=params)
    assert response.status_code == 200
    assert "subscriptions" in response.json()


@pytest.mark.asyncio
async def test_get_subscriptions_pagination_empty_page_returns_200(auth_client_admin: AsyncClient):
    params = {"page": 9999, "limit": 10}
    response = await auth_client_admin.get("/subscriptions", params=params)
    assert response.status_code == 200
    assert len(response.json()["subscriptions"]) == 0


@pytest.mark.asyncio
async def test_create_subscription_admin_success(
    auth_client_admin: AsyncClient, sample_sub_type, normal_user: User
):
    start_date = datetime.date.today().isoformat()
    finish_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    payload = {
        "user_id": normal_user.user_id,
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "subscribe_start": start_date,
        "subscribe_finish": finish_date,
    }
    response = await auth_client_admin.post("/subscriptions", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_create_subscription_for_admin_returns_403(
    auth_client_superadmin: AsyncClient, sample_sub_type, admin_user: User
):
    start_date = datetime.date.today().isoformat()
    finish_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    payload = {
        "user_id": admin_user.user_id,
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "subscribe_start": start_date,
        "subscribe_finish": finish_date,
    }
    response = await auth_client_superadmin.post("/subscriptions", json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_subscription_admin_already_active_returns_400(
    auth_client_admin: AsyncClient,
    sample_sub_type,
    normal_user: User,
    db_session: AsyncSession,
):
    sub = Subscribe(
        user_id=normal_user.user_id,
        subscribe_type_id=sample_sub_type.subscribe_type_id,
        subscribe_start=datetime.date.today(),
        subscribe_finish=datetime.date.today() + datetime.timedelta(days=30),
    )
    db_session.add(sub)
    await db_session.flush()

    start_date = datetime.date.today().isoformat()
    finish_date = (datetime.date.today() + datetime.timedelta(days=60)).isoformat()
    payload = {
        "user_id": normal_user.user_id,
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "subscribe_start": start_date,
        "subscribe_finish": finish_date,
    }
    response = await auth_client_admin.post("/subscriptions", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_subscription_admin_type_not_found_returns_404(
    auth_client_admin: AsyncClient, normal_user: User
):
    start_date = datetime.date.today().isoformat()
    finish_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    payload = {
        "user_id": normal_user.user_id,
        "subscribe_type_id": 999999,
        "subscribe_start": start_date,
        "subscribe_finish": finish_date,
    }
    response = await auth_client_admin.post("/subscriptions", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_subscription_success(
    auth_client_superadmin: AsyncClient,
    db_session: AsyncSession,
    sample_sub_type,
    normal_user: User,
):
    start_date = datetime.date.today()
    sub = Subscribe(
        user_id=normal_user.user_id,
        subscribe_type_id=sample_sub_type.subscribe_type_id,
        subscribe_start=start_date,
        subscribe_finish=start_date + datetime.timedelta(days=30),
    )
    db_session.add(sub)
    await db_session.commit()

    payload = {
        "subscribe_finish": (start_date + datetime.timedelta(days=60)).isoformat()
    }
    response = await auth_client_superadmin.put(
        f"/subscriptions/{normal_user.user_id}/{sample_sub_type.subscribe_type_id}/{start_date.isoformat()}",
        json=payload,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_subscription_not_found_returns_404(auth_client_superadmin: AsyncClient):
    payload = {"subscribe_finish": "2027-01-01"}
    response = await auth_client_superadmin.put(
        "/subscriptions/99999/99999/2025-01-01", json=payload
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_subscription_success(
    auth_client_superadmin: AsyncClient,
    db_session: AsyncSession,
    sample_sub_type,
    normal_user: User,
):
    start_date = datetime.date.today()
    sub = Subscribe(
        user_id=normal_user.user_id,
        subscribe_type_id=sample_sub_type.subscribe_type_id,
        subscribe_start=start_date,
        subscribe_finish=start_date + datetime.timedelta(days=30),
    )
    db_session.add(sub)
    await db_session.commit()

    response = await auth_client_superadmin.patch(
        f"/subscriptions/{normal_user.user_id}/{sample_sub_type.subscribe_type_id}/{start_date.isoformat()}/cancel"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cancel_subscription_not_found_returns_404(auth_client_superadmin: AsyncClient):
    response = await auth_client_superadmin.patch("/subscriptions/99999/99999/2025-01-01/cancel")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::sqlalchemy.exc.SAWarning")
async def test_change_subscription_sp_handled(
    auth_client_admin: AsyncClient,
    normal_user: User,
    sample_sub_type,
    db_session: AsyncSession,
):
    payload = {
        "user_id": normal_user.user_id,
        "subscribe_type_id": sample_sub_type.subscribe_type_id,
        "payment_method": "карта",
    }
    await db_session.begin_nested()
    response = await auth_client_admin.post("/subscriptions/change", json=payload)
    assert response.status_code in [200, 400]