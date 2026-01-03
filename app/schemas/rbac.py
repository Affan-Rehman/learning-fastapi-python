from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    """
    Permission response schema.

    Attributes:
        id: Permission ID
        name: Permission name
        description: Permission description
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """
    Role response schema.

    Attributes:
        id: Role ID
        name: Role name
        description: Role description
        permissions: List of permissions for this role
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: int
    name: str
    description: Optional[str]
    permissions: List[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedRolesResponse(BaseModel):
    """
    Paginated response for role list.

    Attributes:
        items: List of roles
        total: Total number of roles
        skip: Number of roles skipped
        limit: Maximum number of roles per page
    """

    items: List[RoleResponse]
    total: int
    skip: int
    limit: int


class PaginatedPermissionsResponse(BaseModel):
    """
    Paginated response for permission list.

    Attributes:
        items: List of permissions
        total: Total number of permissions
        skip: Number of permissions skipped
        limit: Maximum number of permissions per page
    """

    items: List[PermissionResponse]
    total: int
    skip: int
    limit: int

