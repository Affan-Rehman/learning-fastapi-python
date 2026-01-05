from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, verify_password
from app.rbac.models import Role
from app.users.models import User
from app.users.service import get_user_by_email, get_user_by_username
from app.users.schemas import UserCreate


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    """
    Authenticate user by username/email and password.

    Args:
        db: Database session
        username: Username or email
        password: Plain text password

    Returns:
        User object if authentication succeeds, None otherwise
    """
    user = await get_user_by_username(db, username)
    if not user:
        user = await get_user_by_email(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def create_user(db: AsyncSession, user_data: UserCreate, role_id: int = 2) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user_data: User creation data
        role_id: Role ID to assign (default: 2 for 'user' role)

    Returns:
        Created user object
    """
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role_id=role_id,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .filter(User.id == db_user.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()

