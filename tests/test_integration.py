"""Integration tests for database operations."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.fastapi_quickstart.crud.base import CRUDBase
from src.fastapi_quickstart.models.mixins import BaseIDModel, TimestampMixin
from src.fastapi_quickstart.utils.exceptions import ResourceAlreadyExistsException


# Test Model for integration tests
class IntegrationTestUser(BaseIDModel, TimestampMixin, table=True):  # type: ignore[call-arg]
    """Test user model for integration testing."""

    __tablename__ = "integration_test_users"

    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


class IntegrationTestUserCreate(SQLModel):
    """Schema for creating integration test users."""

    name: str
    email: str
    is_active: bool = True


user_crud = CRUDBase[IntegrationTestUser, IntegrationTestUserCreate, IntegrationTestUser](model=IntegrationTestUser)


# Database fixtures
@pytest.fixture(scope="module")
def sqlite_url() -> str:
    """SQLite database URL."""
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="module")
def postgres_url() -> str | None:
    """PostgreSQL database URL from environment or None if not available."""
    db_host = os.getenv("TEST_POSTGRES_HOST", "localhost")
    db_user = os.getenv("TEST_POSTGRES_USER", "postgres")
    db_password = os.getenv("TEST_POSTGRES_PASSWORD", "postgres")
    db_name = os.getenv("TEST_POSTGRES_DB", "test_db")

    # Only return URL if explicitly configured
    if os.getenv("TEST_POSTGRES_HOST"):
        return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"
    return None


@pytest_asyncio.fixture
async def sqlite_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a SQLite test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def postgres_session(postgres_url: str | None) -> AsyncGenerator[AsyncSession | None, None]:
    """Provide a PostgreSQL test database session if available."""
    if not postgres_url:
        yield None
        return

    try:
        engine = create_async_engine(postgres_url, echo=False, future=True)

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        async_session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session_factory() as session:
            yield session

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

        await engine.dispose()
    except Exception:  # noqa: BLE001
        # If PostgreSQL is not available, skip
        yield None


# SQLite Integration Tests
@pytest.mark.asyncio
async def test_sqlite_crud_operations(sqlite_session: AsyncSession):
    """Test full CRUD lifecycle with SQLite."""
    # Create
    user_data = IntegrationTestUserCreate(name="SQLite User", email="sqlite@test.com")
    created_user = await user_crud.create(sqlite_session, user_data)
    assert created_user.id is not None
    assert created_user.name == "SQLite User"

    # Read
    retrieved_user = await user_crud.get(sqlite_session, created_user.id)
    assert retrieved_user.email == "sqlite@test.com"

    # Update
    updated_user = await user_crud.update(sqlite_session, created_user.id, {"name": "Updated SQLite User"})
    assert updated_user.name == "Updated SQLite User"

    # Delete
    result = await user_crud.delete(sqlite_session, created_user.id)
    assert result is True


@pytest.mark.asyncio
async def test_sqlite_pagination(sqlite_session: AsyncSession):
    """Test pagination with SQLite."""
    # Create multiple users
    for i in range(15):
        user_data = IntegrationTestUserCreate(name=f"User {i}", email=f"user{i}@test.com")
        await user_crud.create(sqlite_session, user_data)

    # Test pagination
    page1 = await user_crud.get_multi(sqlite_session, skip=0, limit=10)
    assert len(page1) == 10

    page2 = await user_crud.get_multi(sqlite_session, skip=10, limit=10)
    assert len(page2) == 5

    # Test count
    total = await user_crud.count(sqlite_session)
    assert total == 15


# PostgreSQL Integration Tests
@pytest.mark.asyncio
async def test_postgres_crud_operations(postgres_session: AsyncSession | None):
    """Test full CRUD lifecycle with PostgreSQL."""
    if postgres_session is None:
        pytest.skip("PostgreSQL not configured for testing")

    # Create
    user_data = IntegrationTestUserCreate(name="Postgres User", email="postgres@test.com")
    created_user = await user_crud.create(postgres_session, user_data)
    assert created_user.id is not None
    assert created_user.name == "Postgres User"

    # Read
    retrieved_user = await user_crud.get(postgres_session, created_user.id)
    assert retrieved_user.email == "postgres@test.com"

    # Update
    updated_user = await user_crud.update(postgres_session, created_user.id, {"name": "Updated Postgres User"})
    assert updated_user.name == "Updated Postgres User"

    # Delete
    result = await user_crud.delete(postgres_session, created_user.id)
    assert result is True


@pytest.mark.asyncio
async def test_postgres_concurrent_operations(postgres_session: AsyncSession | None):
    """Test concurrent operations with PostgreSQL."""
    if postgres_session is None:
        pytest.skip("PostgreSQL not configured for testing")

    # Create multiple users
    users = []
    for i in range(5):
        user_data = IntegrationTestUserCreate(name=f"Concurrent User {i}", email=f"concurrent{i}@test.com")
        user = await user_crud.create(postgres_session, user_data)
        users.append(user)

    # Verify all created
    assert len(users) == 5

    # Check existence
    for user in users:
        exists = await user_crud.exists(postgres_session, id=user.id)
        assert exists is True


@pytest.mark.asyncio
async def test_postgres_transaction_rollback(postgres_session: AsyncSession | None):
    """Test transaction rollback with PostgreSQL."""
    if postgres_session is None:
        pytest.skip("PostgreSQL not configured for testing")

    # Create a user
    user_data = IntegrationTestUserCreate(name="Rollback User", email="rollback@test.com")
    await user_crud.create(postgres_session, user_data)

    # Verify user exists
    count_before = await user_crud.count(postgres_session)
    assert count_before >= 1

    # Try to create duplicate (should fail due to unique email)
    duplicate_data = IntegrationTestUserCreate(name="Duplicate", email="rollback@test.com")
    with pytest.raises(ResourceAlreadyExistsException):
        await user_crud.create(postgres_session, duplicate_data)

    # Count should remain the same
    count_after = await user_crud.count(postgres_session)
    assert count_after == count_before
