from typing import Any, Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class ContentNoChangeException(HTTPException):
    """
    Exception raised when an attempted update operation does not change any data.

    :param detail: Detailed message explaining no change was made.
    :param headers: Optional HTTP headers to be sent in the response.
    """

    def __init__(
        self,
        detail: str = "No changes detected in the content update.",
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class AccessDeniedException(HTTPException, Generic[ModelType]):
    """
    Exception raised when a user attempts to perform an action without the necessary permissions.

    :param detail: Optional detailed message to override the default error message.
    :param headers: Optional HTTP headers to be sent in the response.
    """

    def __init__(
        self, detail: str = "Access denied due to insufficient permissions.", headers: dict[str, Any] | None = None
    ) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)


class ResourceNotFoundException(HTTPException, Generic[ModelType]):
    """
    Exception raised when a specific resource identified by its unique identifier or name is not found.

    :param model: The model class of the resource.
    :param identifier: The unique identifier or name of the resource.
    :param identifier_type: Type of identifier used ('id' or 'name').
    :param headers: Optional HTTP headers to be sent in the response.
    """

    def __init__(
        self,
        model: type[ModelType],
        identifier: str | UUID,
        identifier_type: str = "id",
        headers: dict[str, Any] | None = None,
    ) -> None:
        detail = f"Unable to find the {model.__name__} with {identifier_type} {identifier}."
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class ResourceAlreadyExistsException(HTTPException, Generic[ModelType]):
    """
    Exception raised when attempting to create or update a resource that would violate unique constraints.

    :param model: The model class of the resource.
    :param name: The unique name that already exists.
    :param headers: Optional HTTP headers to be sent in the response.
    """

    def __init__(
        self,
        model: type[ModelType],
        name: str,
        headers: dict[str, Any] | None = None,
    ) -> None:
        detail = f"The {model.__name__} name {name} already exists."
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers)
