from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Attributes:
        items: List of items for current page
        total: Total number of items
        skip: Number of items skipped
        limit: Maximum number of items per page
    """

    items: list[T]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True
