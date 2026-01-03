from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, PermissionChecker
from app.core.rate_limit import limiter, get_rate_limit_config
from app.crud.rbac_service import get_roles, get_permissions
from app.db.session import get_db
from app.models.user import User
from app.schemas.rbac import (
    PaginatedRolesResponse,
    PaginatedPermissionsResponse,
    RoleResponse,
    PermissionResponse,
)
from starlette.requests import Request

router = APIRouter()
rate_limit_config = get_rate_limit_config()


@router.get("/roles", response_model=PaginatedRolesResponse)
@limiter.limit(rate_limit_config["authenticated"])
async def list_roles(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(PermissionChecker("manage_roles")),
    db: AsyncSession = Depends(get_db),
):
    """
    List roles with pagination and search.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        search: Search in role name and description
        current_user: Current authenticated user with manage_roles permission
        db: Database session

    Returns:
        Paginated list of roles
    """
    roles, total = await get_roles(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
    )

    return PaginatedRolesResponse(
        items=[RoleResponse.model_validate(role) for role in roles],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/permissions", response_model=PaginatedPermissionsResponse)
@limiter.limit(rate_limit_config["authenticated"])
async def list_permissions(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(PermissionChecker("manage_roles")),
    db: AsyncSession = Depends(get_db),
):
    """
    List permissions with pagination and search.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        search: Search in permission name and description
        current_user: Current authenticated user with manage_roles permission
        db: Database session

    Returns:
        Paginated list of permissions
    """
    permissions, total = await get_permissions(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
    )

    return PaginatedPermissionsResponse(
        items=[PermissionResponse.model_validate(perm) for perm in permissions],
        total=total,
        skip=skip,
        limit=limit,
    )

