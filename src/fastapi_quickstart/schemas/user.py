from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr


class UserBase(BaseModel):
    """
    Base schema for user-related operations.
    """

    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """

    password: SecretStr


class UserRead(UserBase):
    """
    Schema for reading user data (safe to expose).
    """

    id: UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(UserBase):
    """
    Schema for updating user information.
    Allows partial updates (all fields are optional).
    """

    email: EmailStr | None = None
    password: SecretStr | None = None
