"""Test configuration and fixtures."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.fastapi_quickstart.models.mixins import BaseIDModel, TimestampMixin


# Test Model
class TestUser(BaseIDModel, TimestampMixin, table=True):  # type: ignore[call-arg]
    """Test user model for testing CRUD operations."""

    __tablename__ = "test_users"

    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Provide an in-memory SQLite database URL for testing."""
    return "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def async_engine_fixture(test_db_url: str):
    """Create a test async engine."""
    engine = create_async_engine(test_db_url, echo=False, future=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine_fixture) -> AsyncSession:
    """Provide a test database session."""
    async_session_factory = async_sessionmaker(
        bind=async_engine_fixture,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session
