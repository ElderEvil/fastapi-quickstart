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
    Base class for CRUD (Create, Read, Update, Delete) operations on a SQLModel in a database session.

    :param model: A SQLModel type that represents the database table to perform CRUD operations on.
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
        statement = select(self.model).where(self.model.id == id)
        db_obj = await db_session.exec(statement).first()
        if db_obj is None:
            raise ResourceNotFoundException(self.model, identifier=id)
        return db_obj

    async def get_multi(self, db_session: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Retrieve multiple records with pagination support.

        :param db_session: A database session.
        :param skip: The number of items to skip.
        :param limit: The maximum number of items to return.
        :returns: A list of retrieved items.
        """
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
        """
        db_obj = self.model.model_validate(obj_in)
        try:
            db_session.add(db_obj)
            await db_session.commit()
            await db_session.refresh(db_obj)
        except IntegrityError as e:
            await db_session.rollback()
            raise ResourceAlreadyExistsException(self.model, obj_in.id, headers={"detail": str(e)}) from e
        return db_obj

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
        """
        db_obj = await self.get(db_session, id)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

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
            db_session.add(db_obj)
        else:
            await db_session.delete(db_obj)

        await db_session.commit()
        return True
