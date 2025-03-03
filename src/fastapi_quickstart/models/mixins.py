from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class BaseIDModel(SQLModel):
    """
    Mixin to add an auto-increment integer primary key to a model.
    """

    id: int = Field(
        default=None,
        primary_key=True,
        index=True,
        nullable=False,
        description="Primary key as an auto-increment integer.",
    )


class BaseUUIDModel(SQLModel):
    """
    Mixin to add a UUID primary key to a model.
    """

    id: UUID = Field(
        default_factory=uuid4, primary_key=True, index=True, nullable=False, description="Primary key as a UUID."
    )


class SoftDeleteMixin(SQLModel):
    """
    Mixin to add soft delete functionality to a model.
    """

    is_deleted: bool = Field(default=False, index=True, description="Flag indicating if the record is soft deleted.")
    deleted_at: datetime | None = Field(default=None, description="Timestamp when the record was soft deleted.")

    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        """Restore the record if it was soft deleted."""
        self.is_deleted = False
        self.deleted_at = None


class TimestampMixin(SQLModel):
    """
    Mixin to add timestamp fields to a model.
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False, description="Timestamp when the record was created."
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
        description="Timestamp when the record was last updated.",
    )


class BaseUserMixin(SQLModel):
    """
    Mixin to add standard user fields to a model.
    """

    email: EmailStr
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True, description="Indicates if the user account is active.")
