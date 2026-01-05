from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import (
    create_password_reset_token,
    get_password_hash,
    verify_password,
    verify_password_reset_token,
)
from app.mail.service import send_email_with_template
from app.rbac.models import Role
from app.users.models import User
from app.users.service import get_user_by_email, get_user_by_id, get_user_by_username
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


async def request_password_reset(db: AsyncSession, email: str) -> bool:
    """
    Request password reset by sending reset email to user.

    This function generates a password reset token and sends it via email.
    For security, it always returns True even if the email doesn't exist
    to prevent email enumeration attacks.

    Args:
        db: Database session
        email: User email address

    Returns:
        True (always returns True for security reasons)

    Raises:
        Exception: If email sending fails
    """
    user = await get_user_by_email(db, email)
    if not user:
        return True

    reset_token = create_password_reset_token(email)
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    template_body = {
        "reset_link": reset_link,
        "expiry_minutes": settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
    }

    await send_email_with_template(
        recipients=[email],
        subject="Password Reset Request",
        template_name="password_reset.html",
        template_body=template_body,
    )

    return True


async def reset_password(db: AsyncSession, token: str, new_password: str) -> User:
    """
    Reset user password using reset token.

    Args:
        db: Database session
        token: Password reset token from email
        new_password: New password to set

    Returns:
        Updated user object

    Raises:
        ValueError: If token is invalid or expired
        ValueError: If password doesn't meet strength requirements
    """
    from app.core.security import validate_password_strength

    email = verify_password_reset_token(token)
    if not email:
        raise ValueError("Invalid or expired reset token")

    user = await get_user_by_email(db, email)
    if not user:
        raise ValueError("User not found")

    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        raise ValueError(error_msg)

    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)

    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .filter(User.id == user.id)
    )
    result = await db.execute(stmt)
    updated_user = result.scalar_one()

    template_body = {}
    await send_email_with_template(
        recipients=[email],
        subject="Password Reset Successful",
        template_name="password_reset_success.html",
        template_body=template_body,
    )

    return updated_user


async def change_password(
    db: AsyncSession, user_id: int, old_password: str, new_password: str
) -> User:
    """
    Change user password by verifying old password.

    Args:
        db: Database session
        user_id: User ID
        old_password: Current password for verification
        new_password: New password to set

    Returns:
        Updated user object

    Raises:
        ValueError: If old password is incorrect
        ValueError: If password doesn't meet strength requirements
        ValueError: If user not found
    """
    from app.core.security import validate_password_strength

    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    if not verify_password(old_password, user.hashed_password):
        raise ValueError("Incorrect old password")

    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        raise ValueError(error_msg)

    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)

    stmt = (
        select(User)
        .options(selectinload(User.role).selectinload(Role.permissions))
        .filter(User.id == user_id)
    )
    result = await db.execute(stmt)
    updated_user = result.scalar_one()

    template_body = {"username": user.username}
    await send_email_with_template(
        recipients=[user.email],
        subject="Password Changed Successfully",
        template_name="password_change_success.html",
        template_body=template_body,
    )

    return updated_user

