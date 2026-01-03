from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.rbac import RoleResponse


class UserBase(BaseModel):
    """
    Base user schema with common fields.

    Attributes:
        email: User email address
        username: Username
    """

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """
    Schema for user creation.

    Attributes:
        password: Plain text password (will be hashed)
    """

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """
    Schema for user update (all fields optional).

    Attributes:
        email: New email address
        username: New username
        password: New password
        role_id: New role ID
    """

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    role_id: Optional[int] = None


class UserResponse(UserBase):
    """
    Schema for user response.

    Attributes:
        id: User ID
        role_id: Role ID
        role: Role details
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: int
    role_id: int
    role: Optional[RoleResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedUsersResponse(BaseModel):
    """
    Paginated response for user list.

    Attributes:
        items: List of users
        total: Total number of users
        skip: Number of users skipped
        limit: Maximum number of users per page
    """

    items: List[UserResponse]
    total: int
    skip: int
    limit: int

