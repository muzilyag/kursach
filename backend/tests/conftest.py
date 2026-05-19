import pytest
import pytest_asyncio
import asyncio
from datetime import date
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, async_scoped_session
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from src.main import app
from src.core.database import Base, get_db
from src.models.user import User
from src.core.security import get_password_hash, create_access_token
from src.core.config import settings

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(
        settings.test_database_url, 
        poolclass=NullPool
    )
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
    await engine.dispose()

def current_task_handler():
    try:
        return asyncio.current_task()
    except RuntimeError:
        return None

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    connection = await db_engine.connect()
    trans = await connection.begin()
    
    async_session_factory = async_sessionmaker(
        connection, 
        expire_on_commit=False, 
        class_=AsyncSession
    )
    session = async_session_factory()
    
    yield session
    
    await session.close()
    await trans.rollback()
    await connection.close()

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def normal_user(db_session: AsyncSession) -> User:
    user = User(
        user_name="normal_test",
        user_email="user@test.com",
        user_birth_date=date(1995, 1, 1),
        user_password=get_password_hash("userpass"),
        user_role="user"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        user_name="admin_test",
        user_email="admin@test.com",
        user_birth_date=date(1990, 1, 1),
        user_password=get_password_hash("adminpass"),
        user_role="admin"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def auth_client_user(client: AsyncClient, normal_user: User) -> AsyncClient:
    token = create_access_token(data={"sub": str(normal_user.user_id), "role": normal_user.user_role})
    client.headers["Authorization"] = f"Bearer {token}"
    return client

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def auth_client_admin(client: AsyncClient, admin_user: User) -> AsyncClient:
    token = create_access_token(data={"sub": str(admin_user.user_id), "role": admin_user.user_role})
    client.headers["Authorization"] = f"Bearer {token}"
    return client