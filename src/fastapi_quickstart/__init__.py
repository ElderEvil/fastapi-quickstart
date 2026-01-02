"""FastAPI Quickstart - A package for rapid FastAPI development."""

from fastapi_quickstart.core.config import settings
from fastapi_quickstart.core.db import async_engine, get_async_session
from fastapi_quickstart.crud.base import CRUDBase
from fastapi_quickstart.models.mixins import (
    BaseIDModel,
    BaseUserMixin,
    BaseUUIDModel,
    SoftDeleteMixin,
    TimestampMixin,
)
from fastapi_quickstart.utils.exceptions import (
    AccessDeniedException,
    ContentNoChangeException,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
)

__all__ = [
    # Config
    "settings",
    # Database
    "async_engine",
    "get_async_session",
    # CRUD
    "CRUDBase",
    # Models & Mixins
    "BaseIDModel",
    "BaseUUIDModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "BaseUserMixin",
    # Exceptions
    "AccessDeniedException",
    "ContentNoChangeException",
    "ResourceAlreadyExistsException",
    "ResourceNotFoundException",
]
