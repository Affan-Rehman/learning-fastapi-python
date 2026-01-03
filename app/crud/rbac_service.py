from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permission import Permission
from app.models.role import Role


async def get_role_by_id(db: AsyncSession, role_id: int) -> Role | None:
    """
    Get role by ID with permissions loaded.

    Args:
        db: Database session
        role_id: Role ID

    Returns:
        Role object with permissions, or None if not found
    """
    stmt = select(Role).options(selectinload(Role.permissions)).filter(Role.id == role_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    """
    Get role by name with permissions loaded.

    Args:
        db: Database session
        name: Role name

    Returns:
        Role object with permissions, or None if not found
    """
    stmt = select(Role).options(selectinload(Role.permissions)).filter(Role.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_roles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
) -> tuple[list[Role], int]:
    """
    Get paginated list of roles with search.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search in role name and description

    Returns:
        Tuple of (list of roles, total count)
    """
    stmt = select(Role).options(selectinload(Role.permissions))

    if search:
        stmt = stmt.filter(
            or_(
                Role.name.ilike(f"%{search}%"),
                Role.description.ilike(f"%{search}%"),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    stmt = stmt.order_by(Role.id.asc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    roles = result.scalars().all()

    return list(roles), total


async def get_permission_by_id(db: AsyncSession, permission_id: int) -> Permission | None:
    """
    Get permission by ID.

    Args:
        db: Database session
        permission_id: Permission ID

    Returns:
        Permission object, or None if not found
    """
    stmt = select(Permission).filter(Permission.id == permission_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_permission_by_name(db: AsyncSession, name: str) -> Permission | None:
    """
    Get permission by name.

    Args:
        db: Database session
        name: Permission name

    Returns:
        Permission object, or None if not found
    """
    stmt = select(Permission).filter(Permission.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_permissions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
) -> tuple[list[Permission], int]:
    """
    Get paginated list of permissions with search.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search in permission name and description

    Returns:
        Tuple of (list of permissions, total count)
    """
    stmt = select(Permission)

    if search:
        stmt = stmt.filter(
            or_(
                Permission.name.ilike(f"%{search}%"),
                Permission.description.ilike(f"%{search}%"),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    stmt = stmt.order_by(Permission.id.asc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    permissions = result.scalars().all()

    return list(permissions), total
