import pytest
import datetime
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.models.subscription import SubscribeType, Subscribe
from src.models.payment import Payment
from src.models.content import Content, Genre, Tag, CopyrightHolder
from src.models.viewing import Viewing


@pytest.mark.asyncio
async def test_get_dashboard_statistics_unauthorized_returns_401(client: AsyncClient):
    response = await client.get("/stats")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_dashboard_statistics_forbidden_for_user_returns_403(auth_client_user: AsyncClient):
    response = await auth_client_user.get("/stats")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_dashboard_statistics_admin_empty_db_success(auth_client_admin: AsyncClient):
    response = await auth_client_admin.get("/stats")
    assert response.status_code == 200
    assert "total_users" in response.json()
    assert (
        response.json()["breakdown"]["registrations_dynamics"]["growth_percentage"]
        == 0.0
    )


@pytest.mark.asyncio
async def test_get_dashboard_statistics_populated_db_success(
    auth_client_admin: AsyncClient, db_session: AsyncSession, normal_user: User
):
    sub_type = SubscribeType(
        subscribe_type_name="Stats Premium",
        subscribe_type_discription="All access",
        subscribe_type_max_type_quality=4,
        subscribe_type_cost=Decimal("500.00"),
        subscribe_type_duration=30,
    )
    db_session.add(sub_type)
    await db_session.flush()

    sub = Subscribe(
        user_id=normal_user.user_id,
        subscribe_type_id=sub_type.subscribe_type_id,
        subscribe_start=datetime.date.today() - datetime.timedelta(days=10),
        subscribe_finish=datetime.date.today() + datetime.timedelta(days=20),
    )
    payment = Payment(
        user_id=normal_user.user_id,
        payment_number=1,
        subscribe_type_id=sub_type.subscribe_type_id,
        subscribe_start=sub.subscribe_start,
        payment_date=datetime.date.today() - datetime.timedelta(days=10),
        payment_sum=Decimal("500.00"),
        payment_method="карта",
    )

    genre = Genre(genre_name="StatsGenre")
    tag = Tag(tag_name="StatsTag")
    holder = CopyrightHolder(
        copyright_holder_name="StatsHolder",
        copyright_holder_phone="123",
        copyright_holder_email="a@a.com",
    )

    content = Content(
        content_name="StatsMovie",
        content_type="movie",
        content_duration=datetime.time(1, 0),
        content_publish_date=datetime.date(2025, 1, 1),
    )

    db_session.add_all([sub, payment, genre, tag, holder, content])
    await db_session.flush()

    viewing = Viewing(
        user_id=normal_user.user_id,
        content_id=content.content_id,
        viewing_progress=50,
        viewing_start=datetime.datetime(2025, 1, 1, 1, 0),
        viewing_finish=datetime.datetime(2025, 1, 1, 1, 30),
    )
    db_session.add(viewing)

    past_user = User(
        user_name="past_user",
        user_email="past@test.com",
        user_birth_date=datetime.date(1990, 1, 1),
        user_password="hashed_password",
        user_registration_date=datetime.date.today() - datetime.timedelta(days=10),
        user_role="user",
    )
    db_session.add(past_user)
    await db_session.commit()

    response = await auth_client_admin.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert float(data["total_revenue"]) >= 500.0
    assert data["total_content"] >= 1
    assert data["total_genres"] >= 1
    assert data["total_tags"] >= 1
    assert data["total_copyright_holders"] >= 1
    assert data["total_viewings"] >= 1
    assert data["breakdown"]["subscriptions_status"]["active"] >= 1
    assert any(
        t["tariff_name"] == "Stats Premium"
        for t in data["breakdown"]["revenue_by_tariffs"]
    )