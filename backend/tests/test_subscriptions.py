import pytest
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.subscription import SubscribeType

@pytest.mark.asyncio
async def test_get_subscription_types(client: AsyncClient, db_session: AsyncSession):
    sub_type = SubscribeType(
        subscribe_type_name="Premium",
        subscribe_type_discription="All access",
        subscribe_type_max_type_quality=4,
        subscribe_type_cost=Decimal("299.00"),
        subscribe_type_duration=30
    )
    db_session.add(sub_type)
    await db_session.commit()
    response = await client.get("/subscriptions/types")
    assert response.status_code == 200
    assert len(response.json()) >= 1

@pytest.mark.asyncio
async def test_buy_subscription(auth_client_user: AsyncClient, db_session: AsyncSession):
    sub_type = SubscribeType(
        subscribe_type_name="Standard",
        subscribe_type_discription="HD access",
        subscribe_type_max_type_quality=2,
        subscribe_type_cost=Decimal("199.00"),
        subscribe_type_duration=30
    )
    db_session.add(sub_type)
    await db_session.commit()
    payload = {"subscribe_type_id": sub_type.subscribe_type_id}
    response = await auth_client_user.post("/subscriptions/buy", json=payload)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_preview_subscription_change(auth_client_user: AsyncClient, db_session: AsyncSession):
    sub_type = SubscribeType(
        subscribe_type_name="Premium Extra",
        subscribe_type_discription="Ultra HD access",
        subscribe_type_max_type_quality=4,
        subscribe_type_cost=Decimal("399.00"),
        subscribe_type_duration=30
    )
    db_session.add(sub_type)
    await db_session.flush()

    url = f"/subscriptions/preview-change?target_type_id={sub_type.subscribe_type_id}"
    response = await auth_client_user.get(url)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_buy_subscription_not_found(auth_client_user: AsyncClient):
    payload = {"subscribe_type_id": 9999}
    response = await auth_client_user.post("/subscriptions/buy", json=payload)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_subscription_types_empty(client: AsyncClient):
    response = await client.get("/subscriptions/types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)