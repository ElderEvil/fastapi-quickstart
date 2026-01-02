"""Tests for CRUD operations."""

import pytest
from sqlmodel import Field, SQLModel

from src.fastapi_quickstart.crud.base import CRUDBase
from src.fastapi_quickstart.models.mixins import BaseIDModel, SoftDeleteMixin, TimestampMixin
from src.fastapi_quickstart.utils.exceptions import ResourceNotFoundException
from tests.conftest import TestUser

# Test CRUD instance
user_crud = CRUDBase[TestUser, TestUser, TestUser](model=TestUser)


class TestUserCreate(SQLModel):
    """Schema for creating test users."""

    name: str
    email: str
    is_active: bool = True


class TestUserUpdate(SQLModel):
    """Schema for updating test users."""

    name: str | None = None
    email: str | None = None
    is_active: bool | None = None


# Soft delete test model
class TestProduct(BaseIDModel, TimestampMixin, SoftDeleteMixin, table=True):  # type: ignore[call-arg]
    """Test product model with soft delete."""

    __tablename__ = "test_products"

    name: str = Field(max_length=100)
    price: float


class TestProductCreate(SQLModel):
    """Schema for creating test products."""

    name: str
    price: float


product_crud = CRUDBase[TestProduct, TestProductCreate, TestProduct](model=TestProduct)


@pytest.mark.asyncio
async def test_create_user(async_session):
    """Test creating a new user."""
    user_data = TestUserCreate(name="John Doe", email="john@example.com")
    user = await user_crud.create(async_session, user_data)

    assert user.id is not None
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.asyncio
async def test_get_user(async_session):
    """Test retrieving a user by ID."""
    user_data = TestUserCreate(name="Jane Doe", email="jane@example.com")
    created_user = await user_crud.create(async_session, user_data)

    retrieved_user = await user_crud.get(async_session, created_user.id)

    assert retrieved_user.id == created_user.id
    assert retrieved_user.name == created_user.name
    assert retrieved_user.email == created_user.email


@pytest.mark.asyncio
async def test_get_nonexistent_user(async_session):
    """Test retrieving a user that doesn't exist."""
    with pytest.raises(ResourceNotFoundException):
        await user_crud.get(async_session, 99999)


@pytest.mark.asyncio
async def test_get_multi_users(async_session):
    """Test retrieving multiple users."""
    users_data = [
        TestUserCreate(name="User 1", email="user1@example.com"),
        TestUserCreate(name="User 2", email="user2@example.com"),
        TestUserCreate(name="User 3", email="user3@example.com"),
    ]

    for user_data in users_data:
        await user_crud.create(async_session, user_data)

    users = await user_crud.get_multi(async_session, skip=0, limit=10)

    assert len(users) == 3
    assert users[0].name == "User 1"
    assert users[2].name == "User 3"


@pytest.mark.asyncio
async def test_get_multi_with_pagination(async_session):
    """Test pagination with get_multi."""
    for i in range(5):
        user_data = TestUserCreate(name=f"User {i}", email=f"user{i}@example.com")
        await user_crud.create(async_session, user_data)

    # Get first page
    users_page1 = await user_crud.get_multi(async_session, skip=0, limit=2)
    assert len(users_page1) == 2

    # Get second page
    users_page2 = await user_crud.get_multi(async_session, skip=2, limit=2)
    assert len(users_page2) == 2

    # Ensure different users
    assert users_page1[0].id != users_page2[0].id


@pytest.mark.asyncio
async def test_count_users(async_session):
    """Test counting users."""
    assert await user_crud.count(async_session) == 0

    for i in range(3):
        user_data = TestUserCreate(name=f"User {i}", email=f"user{i}@example.com")
        await user_crud.create(async_session, user_data)

    assert await user_crud.count(async_session) == 3


@pytest.mark.asyncio
async def test_update_user(async_session):
    """Test updating a user."""
    user_data = TestUserCreate(name="Old Name", email="old@example.com")
    created_user = await user_crud.create(async_session, user_data)

    update_data = TestUserUpdate(name="New Name")
    updated_user = await user_crud.update(async_session, created_user.id, update_data)

    assert updated_user.id == created_user.id
    assert updated_user.name == "New Name"
    assert updated_user.email == "old@example.com"  # Unchanged


@pytest.mark.asyncio
async def test_exists_user(async_session):
    """Test checking if a user exists."""
    user_data = TestUserCreate(name="Exists Test", email="exists@example.com")
    await user_crud.create(async_session, user_data)

    assert await user_crud.exists(async_session, email="exists@example.com") is True
    assert await user_crud.exists(async_session, email="notexists@example.com") is False


@pytest.mark.asyncio
async def test_delete_user(async_session):
    """Test deleting a user."""
    user_data = TestUserCreate(name="To Delete", email="delete@example.com")
    created_user = await user_crud.create(async_session, user_data)

    result = await user_crud.delete(async_session, created_user.id)
    assert result is True

    with pytest.raises(ResourceNotFoundException):
        await user_crud.get(async_session, created_user.id)


@pytest.mark.asyncio
async def test_delete_nonexistent_user(async_session):
    """Test deleting a user that doesn't exist."""
    with pytest.raises(ResourceNotFoundException):
        await user_crud.delete(async_session, 99999)


@pytest.mark.asyncio
async def test_soft_delete_product(async_session):
    """Test soft deleting a product."""
    product_data = TestProductCreate(name="Test Product", price=99.99)
    created_product = await product_crud.create(async_session, product_data)

    result = await product_crud.delete(async_session, created_product.id, soft_delete=True)
    assert result is True

    # Product should still be retrievable but marked as deleted
    soft_deleted_product = await product_crud.get(async_session, created_product.id)
    assert soft_deleted_product.is_deleted is True
    assert soft_deleted_product.deleted_at is not None


@pytest.mark.asyncio
async def test_get_or_create_new_user(async_session):
    """Test get_or_create when user doesn't exist."""
    user_data = TestUserCreate(name="New User", email="new@example.com")
    user, created = await user_crud.get_or_create(async_session, user_data, email="new@example.com")

    assert created is True
    assert user.id is not None
    assert user.name == "New User"
    assert user.email == "new@example.com"


@pytest.mark.asyncio
async def test_get_or_create_existing_user(async_session):
    """Test get_or_create when user already exists."""
    # Create a user first
    user_data = TestUserCreate(name="Existing User", email="existing@example.com")
    existing_user = await user_crud.create(async_session, user_data)

    # Try to get_or_create with same email
    new_data = TestUserCreate(name="Different Name", email="existing@example.com")
    user, created = await user_crud.get_or_create(async_session, new_data, email="existing@example.com")

    assert created is False
    assert user.id == existing_user.id
    assert user.name == "Existing User"  # Should keep original name
    assert user.email == "existing@example.com"


@pytest.mark.asyncio
async def test_get_or_create_no_filters(async_session):
    """Test get_or_create raises error when no filters provided."""
    user_data = TestUserCreate(name="Test User", email="test@example.com")

    with pytest.raises(ValueError, match="At least one filter must be provided"):
        await user_crud.get_or_create(async_session, user_data)
