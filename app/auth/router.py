from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    PasswordResetResponse,
    ResetPasswordRequest,
    Token,
    UserRegister,
)
from app.auth.service import (
    authenticate_user,
    change_password,
    create_user,
    request_password_reset,
    reset_password,
)
from app.core.rate_limit import get_rate_limit_config, limiter
from app.core.security import create_access_token, validate_password_strength
from app.db.session import get_db
from app.users.models import User
from app.users.service import get_user_by_email, get_user_by_username
from app.users.schemas import UserResponse

router = APIRouter()
rate_limit_config = get_rate_limit_config()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit(rate_limit_config["auth_endpoints"])
async def register(
    request: Request,
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: 400 if email/username already exists or password is weak
    """
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = await create_user(db, user_data)
    access_token = create_access_token(data={"sub": user.id})

    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
@limiter.limit(rate_limit_config["auth_endpoints"])
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Login user and return JWT token.

    Args:
        form_data: OAuth2 password request form (username, password)
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
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


@router.post("/forgot-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["auth_endpoints"])
async def forgot_password(
    request: Request,
    forgot_password_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset by email.

    Sends a password reset email to the user if the email exists.
    For security reasons, always returns success message even if email doesn't exist
    to prevent email enumeration attacks.

    Args:
        request: FastAPI request object
        forgot_password_data: Email address for password reset
        db: Database session

    Returns:
        Success message (always returns success for security)

    Example:
        ```json
        {
            "email": "user@example.com"
        }
        ```
    """
    try:
        await request_password_reset(db, forgot_password_data.email)
    except Exception:
        pass

    return PasswordResetResponse(
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
@limiter.limit(rate_limit_config["auth_endpoints"])
async def reset_password_endpoint(
    request: Request,
    reset_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using reset token from email.

    Validates the reset token and updates the user's password.
    Sends a confirmation email after successful password reset.

    Args:
        request: FastAPI request object
        reset_data: Reset token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 400 if token is invalid/expired or password is weak
        HTTPException: 404 if user not found

    Example:
        ```json
        {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "new_password": "NewSecurePassword123!"
        }
        ```
    """
    try:
        await reset_password(db, reset_data.token, reset_data.new_password)
    except ValueError as e:
        error_msg = str(e)
        if "Invalid or expired" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        elif "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

    return PasswordResetResponse(message="Password has been reset successfully")


@router.post("/change-password", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def change_password_endpoint(
    change_password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change password for authenticated user.

    Verifies the old password before updating to the new password.
    Sends a confirmation email after successful password change.

    Args:
        change_password_data: Old password and new password
        current_user: Current authenticated user (from dependency)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 400 if old password is incorrect or new password is weak
        HTTPException: 404 if user not found

    Example:
        ```json
        {
            "old_password": "CurrentPassword123!",
            "new_password": "NewSecurePassword123!"
        }
        ```
    """
    try:
        await change_password(
            db, current_user.id, change_password_data.old_password, change_password_data.new_password
        )
    except ValueError as e:
        error_msg = str(e)
        if "Incorrect old password" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password",
            )
        elif "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

    return PasswordResetResponse(message="Password has been changed successfully")

