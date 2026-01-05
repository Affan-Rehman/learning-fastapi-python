from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.auth.dependencies import get_current_user
from app.core.dependencies import PermissionChecker
from app.core.rate_limit import get_rate_limit_config, limiter
from app.db.session import get_db
from app.users.models import User
from app.users.schemas import PaginatedUsersResponse, UserResponse, UserUpdate
from app.users.service import delete_user, get_user_by_id, get_users, update_user

router = APIRouter()
rate_limit_config = get_rate_limit_config()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user (from dependency)

    Returns:
        Current user information
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit(rate_limit_config["authenticated"])
async def get_user(
    request: Request,
    user_id: int,
    current_user: User = Depends(PermissionChecker("read_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID.

    Args:
        user_id: User ID
        current_user: Current authenticated user with read_user permission
        db: Database session

    Returns:
        User information

    Raises:
        HTTPException: 404 if user not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("", response_model=PaginatedUsersResponse)
@limiter.limit(rate_limit_config["authenticated"])
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    email: str | None = Query(None),
    username: str | None = Query(None),
    role_id: int | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("id"),
    order: str = Query("asc"),
    current_user: User = Depends(PermissionChecker("read_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    List users with pagination, filtering, searching, and sorting.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        email: Filter by email
        username: Filter by username
        role_id: Filter by role ID
        search: Search in email and username
        sort_by: Field to sort by
        order: Sort order (asc/desc)
        current_user: Current authenticated user with read_user permission
        db: Database session

    Returns:
        Paginated list of users
    """
    users, total = await get_users(
        db=db,
        skip=skip,
        limit=limit,
        email=email,
        username=username,
        role_id=role_id,
        search=search,
        sort_by=sort_by,
        order=order,
    )

    return PaginatedUsersResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.put("/{user_id}", response_model=UserResponse)
@limiter.limit(rate_limit_config["authenticated"])
async def update_user_endpoint(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(PermissionChecker("update_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user information.

    Args:
        user_id: User ID to update
        user_data: User update data
        current_user: Current authenticated user with update_user permission
        db: Database session

    Returns:
        Updated user information

    Raises:
        HTTPException: 404 if user not found
    """
    user = await update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(rate_limit_config["authenticated"])
async def delete_user_endpoint(
    request: Request,
    user_id: int,
    current_user: User = Depends(PermissionChecker("delete_user")),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user.

    Args:
        user_id: User ID to delete
        current_user: Current authenticated user with delete_user permission
        db: Database session

    Raises:
        HTTPException: 404 if user not found
    """
    deleted = await delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
