import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.rate_limit import setup_rate_limiting
from app.db.session import engine
from app.schemas import (
    PaginatedPermissionsResponse,
    PaginatedRolesResponse,
    PaginatedUsersResponse,
    PermissionResponse,
    RoleResponse,
    UserResponse,
)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if settings.LOG_FORMAT == "text"
    else None,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Replaces deprecated @app.on_event decorators.

    Args:
        app: FastAPI application instance
    """
    try:
        async with engine.begin() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=5.0)
        logging.info("Database connection verified")
    except asyncio.TimeoutError:
        logging.warning("Database connection timeout during startup - continuing anyway")
    except Exception as e:
        logging.warning(f"Database connection check failed during startup: {e} - continuing anyway")

    yield

    await engine.dispose()
    logging.info("Database connections closed")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend with RBAC (Role-Based Access Control)",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_rate_limiting(app)

for model in [
    UserResponse,
    PaginatedUsersResponse,
    RoleResponse,
    PaginatedRolesResponse,
    PermissionResponse,
    PaginatedPermissionsResponse,
]:
    model.model_rebuild()

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom validation error handler.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSON response with validation errors
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    General exception handler.

    Args:
        request: FastAPI request object
        exc: Exception

    Returns:
        JSON response with error message
    """
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
    }
