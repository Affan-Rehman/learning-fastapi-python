from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.rbac.models import Role
from app.users.models import User
from app.users.schemas import UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Get user by ID with role and permissions loaded.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object with role and permissions, or None if not found
    """
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .filter(User.id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Get user by email with role and permissions loaded.

    Args:
        db: Database session
        email: User email

    Returns:
        User object with role and permissions, or None if not found
    """
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .filter(User.email == email)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    Get user by username with role and permissions loaded.

    Args:
        db: Database session
        username: Username

    Returns:
        User object with role and permissions, or None if not found
    """
    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .filter(User.username == username)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User | None:
    """
    Update user information.

    Args:
        db: Database session
        user_id: User ID to update
        user_data: User update data

    Returns:
        Updated user object with role and permissions, or None if not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .filter(User.id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Delete a user.

    Args:
        db: Database session
        user_id: User ID to delete

    Returns:
        True if user was deleted, False if not found
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False

    await db.delete(user)
    await db.commit()
    return True


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    email: str | None = None,
    username: str | None = None,
    role_id: int | None = None,
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> tuple[list[User], int]:
    """
    Get paginated list of users with filtering, searching, and sorting.

    Uses eager loading to prevent N+1 problems.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        email: Filter by email
        username: Filter by username
        role_id: Filter by role ID
        search: Search in email and username
        sort_by: Field to sort by
        order: Sort order (asc/desc)

    Returns:
        Tuple of (list of users, total count)
    """
    stmt = select(User).options(selectinload(User.role).selectinload(Role.permissions))

    if email:
        stmt = stmt.filter(User.email == email)
    if username:
        stmt = stmt.filter(User.username == username)
    if role_id:
        stmt = stmt.filter(User.role_id == role_id)
    if search:
        stmt = stmt.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    sort_column = getattr(User, sort_by, User.id)
    if order.lower() == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return list(users), total

