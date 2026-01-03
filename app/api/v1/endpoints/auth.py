from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter, get_rate_limit_config
from app.core.security import create_access_token, validate_password_strength
from app.crud.user_service import create_user, authenticate_user, get_user_by_email, get_user_by_username
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserResponse

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

