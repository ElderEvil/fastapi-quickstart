"""
Base CRUD operations for SQLModel-based database tables.

This module provides a generic, type-safe base class for performing common database
operations (Create, Read, Update, Delete) on SQLModel tables. It handles async operations,
error handling, pagination, and soft deletion.

Example Usage:
    ```python
    from sqlmodel import Field, SQLModel
    from fastapi_quickstart.crud.base import CRUDBase
    from fastapi_quickstart.models.mixins import BaseIDModel

    # Define your model
    class User(BaseIDModel, table=True):
        name: str = Field(max_length=100)
        email: str = Field(unique=True)

    # Define schemas
    class UserCreate(SQLModel):
        name: str
        email: str

    class UserUpdate(SQLModel):
        name: str | None = None
        email: str | None = None

    # Create CRUD instance
    user_crud = CRUDBase[User, UserCreate, UserUpdate](model=User)

    # Use in your endpoints
    async def create_user(user_data: UserCreate, session: AsyncSession):
        return await user_crud.create(session, user_data)

    # Get or create user by email
    async def get_or_create_user(user_data: UserCreate, session: AsyncSession):
        user, created = await user_crud.get_or_create(session, user_data, email=user_data.email)
        return user, created
    ```

Type Parameters:
    ModelType: The SQLModel table class
    CreateSchemaType: Schema for creating new records
    UpdateSchemaType: Schema for updating existing records
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.fastapi_quickstart.utils.exceptions import ResourceAlreadyExistsException, ResourceNotFoundException

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base class for CRUD operations on SQLModel tables.

    This class provides type-safe, async database operations with consistent error handling,
    validation, and support for soft deletion. All methods are designed to work with
    SQLModel's async session.

    Type Parameters:
        ModelType: The SQLModel table class (must have an 'id' field)
        CreateSchemaType: Pydantic/SQLModel schema for creating records
        UpdateSchemaType: Pydantic/SQLModel schema for updating records

    Attributes:
        model: The SQLModel class this CRUD instance operates on

    Example:
        ```python
        from fastapi_quickstart.crud.base import CRUDBase
        from myapp.models import User
        from myapp.schemas import UserCreate, UserUpdate

        user_crud = CRUDBase[User, UserCreate, UserUpdate](model=User)

        # Create a user
        user = await user_crud.create(session, UserCreate(name="Alice", email="alice@example.com"))

        # Get a user
        user = await user_crud.get(session, user_id=1)

        # Update a user
        updated = await user_crud.update(session, user_id=1, obj_in={"name": "Alice Smith"})

        # Delete a user
        await user_crud.delete(session, user_id=1)

        # Get or create user by email
        user, created = await user_crud.get_or_create(
            session,
            UserCreate(name="Alice", email="alice@example.com"),
            email="alice@example.com"
        )
        ```

    API Contract:
        - All operations are async and require an AsyncSession
        - Models must have an 'id' attribute (use BaseIDModel or BaseUUIDModel)
        - create() validates input and handles IntegrityError
        - get() raises ResourceNotFoundException if not found
        - update() validates fields exist on the model
        - delete() supports soft deletion if model has SoftDeleteMixin
        - All database errors are properly rolled back
    """

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db_session: AsyncSession, id: int | UUID) -> ModelType:
        """
        Retrieve a single item by its ID.

        :param db_session: A database session.
        :param id: The ID of an object to retrieve.
        :returns: The retrieved item.
        :raises ResourceNotFoundException: If the item does not exist.
        """
        if not hasattr(self.model, "id"):
            msg = f"Model {self.model.__name__} does not have an 'id' attribute"
            raise AttributeError(msg)

        statement = select(self.model).where(self.model.id == id)
        result = await db_session.exec(statement)
        db_obj = result.first()
        if db_obj is None:
            raise ResourceNotFoundException(self.model, identifier=id)
        return db_obj

    async def get_multi(self, db_session: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Retrieve multiple records with pagination support.

        :param db_session: A database session.
        :param skip: The number of items to skip (must be non-negative).
        :param limit: The maximum number of items to return (must be positive).
        :returns: A list of retrieved items.
        :raises ValueError: If skip is negative or limit is non-positive.
        """
        if skip < 0:
            msg = "skip must be non-negative"
            raise ValueError(msg)
        if limit <= 0:
            msg = "limit must be positive"
            raise ValueError(msg)

        if not hasattr(self.model, "id"):
            msg = f"Model {self.model.__name__} does not have an 'id' attribute"
            raise AttributeError(msg)

        statement = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        return (await db_session.exec(statement)).all()

    async def count(self, db_session: AsyncSession) -> int:
        """
        Get the count of records in the database.

        :param db_session: A database session.
        :returns: The number of records.
        """
        return (await db_session.exec(select(func.count()).select_from(self.model))).one()

    async def create(self, db_session: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        :param db_session: A database session.
        :param obj_in: The item to create.
        :returns: The created object.
        :raises ResourceAlreadyExistsException: If the item already exists.
        :raises ValueError: If validation fails.
        """
        db_obj = self.model.model_validate(obj_in)
        try:
            db_session.add(db_obj)
            await db_session.commit()
            await db_session.refresh(db_obj)
        except IntegrityError as e:
            await db_session.rollback()
            # Try to get ID from obj_in if it has one
            obj_id = getattr(obj_in, "id", None)
            raise ResourceAlreadyExistsException(self.model, obj_id, headers={"detail": str(e)}) from e
        return db_obj

    async def get_or_create(
        self, db_session: AsyncSession, obj_in: CreateSchemaType, **filters: Any
    ) -> tuple[ModelType, bool]:
        """
        Get an existing record or create it if it doesn't exist.

        This method first attempts to find a record matching the provided filters.
        If found, it returns the existing record. If not found, it creates a new
        record using the provided data.

        :param db_session: A database session.
        :param obj_in: The item data to create if the record doesn't exist.
        :param filters: Key-value pairs to filter and find existing records.
        :returns: A tuple of (object, created) where created is True if a new record was created.
        :raises ValueError: If no filters are provided.
        :raises IntegrityError: If creation fails due to constraint violations.

        Example:
            ```python
            # Get or create user by email
            user, created = await user_crud.get_or_create(
                session,
                UserCreate(name="Alice", email="alice@example.com"),
                email="alice@example.com"
            )

            if created:
                print("New user created!")
            else:
                print("User already exists!")
            ```

        API Contract:
            - At least one filter must be provided
            - Filters are used with AND logic (all must match)
            - If multiple records match, returns the first one
            - Creation uses the same validation as create()
            - The operation is not atomic; use with appropriate isolation level
        """
        if not filters:
            msg = "At least one filter must be provided for get_or_create"
            raise ValueError(msg)

        # Try to find existing record
        statement = select(self.model).filter_by(**filters)
        result = await db_session.exec(statement)
        existing = result.first()

        if existing:
            return existing, False

        # Create new record if not found
        db_obj = await self.create(db_session, obj_in)
        return db_obj, True

    async def update(
        self, db_session: AsyncSession, id: int | UUID, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.

        :param db_session: A database session.
        :param id: The ID of the object to update.
        :param obj_in: The updated data as a SQLModel instance or dictionary.
        :returns: The updated item.
        :raises ResourceNotFoundException: If the item does not exist.
        :raises ValueError: If update data is empty.
        """
        db_obj = await self.get(db_session, id)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        if not update_data:
            msg = "No data provided for update"
            raise ValueError(msg)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
            else:
                msg = f"Model {self.model.__name__} does not have attribute '{field}'"
                raise AttributeError(msg)

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def exists(self, db_session: AsyncSession, **filters: Any) -> bool:
        """
        Check if a record exists matching the given filters.

        :param db_session: A database session.
        :param filters: Key-value pairs to filter the records.
        :returns: True if a record exists, otherwise False.
        """
        count = (await db_session.exec(select(func.count()).select_from(self.model).filter_by(**filters))).one()
        return count > 0

    async def delete(self, db_session: AsyncSession, id: int | UUID, *, soft_delete: bool = False) -> bool:
        """
        Delete a record from the database. Supports soft deletion if the model has a `deleted_at` column.

        :param db_session: A database session.
        :param id: The ID of the object to remove.
        :param soft_delete: If True, marks the record as deleted instead of removing it.
        :returns: True if deletion was successful, otherwise False.
        """
        db_obj = await self.get(db_session, id)
        if not db_obj:
            return False

        if soft_delete and hasattr(db_obj, "deleted_at"):
            db_obj.deleted_at = datetime.now(tz=UTC)
            if hasattr(db_obj, "is_deleted"):
                db_obj.is_deleted = True
            db_session.add(db_obj)
        else:
            await db_session.delete(db_obj)

        await db_session.commit()
        return True
