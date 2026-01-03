from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.

    Attributes:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 10, max: 100)
    """

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of records to return")

    @field_validator("skip")
    @classmethod
    def validate_skip(cls, v: int) -> int:
        if v < 0:
            raise ValueError("skip must be non-negative")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("limit must be between 1 and 100")
        return v


class SortOrder(str):
    """
    Sort order enumeration.
    """

    ASC = "asc"
    DESC = "desc"


class SortParams(BaseModel):
    """
    Sorting parameters for list endpoints.

    Attributes:
        sort_by: Field name to sort by (default: "id")
        order: Sort order - "asc" or "desc" (default: "asc")
    """

    sort_by: str = Field(default="id", description="Field name to sort by")
    order: str = Field(default="asc", description="Sort order: asc or desc")

    @field_validator("order")
    @classmethod
    def validate_order(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in ["asc", "desc"]:
            raise ValueError("order must be 'asc' or 'desc'")
        return v_lower


class SearchParams(BaseModel):
    """
    Search parameters for text search across multiple fields.

    Attributes:
        search: Search query string
    """

    search: Optional[str] = Field(default=None, description="Search query string")


class UserFilterParams(BaseModel):
    """
    Filter parameters for user list endpoint.

    Attributes:
        email: Filter by email address
        username: Filter by username
        role_id: Filter by role ID
    """

    email: Optional[str] = Field(default=None, description="Filter by email address")
    username: Optional[str] = Field(default=None, description="Filter by username")
    role_id: Optional[int] = Field(default=None, description="Filter by role ID")

