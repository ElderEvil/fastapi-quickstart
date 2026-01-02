"""FastAPI Quickstart - A package for rapid FastAPI development."""

from src.fastapi_quickstart.core.config import settings
from src.fastapi_quickstart.core.db import async_engine, get_async_session
from src.fastapi_quickstart.crud.base import CRUDBase
from src.fastapi_quickstart.models.mixins import (
    BaseIDModel,
    BaseUserMixin,
    BaseUUIDModel,
    SoftDeleteMixin,
    TimestampMixin,
)
from src.fastapi_quickstart.utils.exceptions import (
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
