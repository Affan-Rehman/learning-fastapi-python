from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


def get_rate_limit_config() -> dict:
    """
    Get rate limit configuration from settings.

    Returns:
        Dictionary with rate limit configurations
    """
    return {
        "authenticated": f"{settings.RATE_LIMIT_AUTHENTICATED}/minute",
        "unauthenticated": f"{settings.RATE_LIMIT_UNAUTHENTICATED}/minute",
        "auth_endpoints": f"{settings.RATE_LIMIT_AUTH_ENDPOINTS}/minute",
    }


def setup_rate_limiting(app):
    """
    Set up rate limiting middleware for the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    if settings.RATE_LIMIT_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        return limiter
    return None
