from datetime import datetime

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
    description: str | None
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
    description: str | None
    permissions: list[PermissionResponse] = []
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

    items: list[RoleResponse]
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

    items: list[PermissionResponse]
    total: int
    skip: int
    limit: int

