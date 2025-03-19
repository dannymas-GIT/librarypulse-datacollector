from typing import Optional, Dict, Any
from fastapi import Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

# Create rate limiter with memory storage for tests
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT]
)

# Rate limit rules
RATE_LIMIT_RULES: Dict[str, str] = {
    # Authentication endpoints
    "/api/v1/auth/login": settings.RATE_LIMIT_LOGIN,
    "/api/v1/auth/register": settings.RATE_LIMIT_REGISTER,
    "/api/v1/auth/forgot-password": settings.RATE_LIMIT_PASSWORD_RESET,
    "/api/v1/auth/verify-email": settings.RATE_LIMIT_EMAIL_VERIFY,
    "/api/v1/auth/reset-password": settings.RATE_LIMIT_EMAIL_VERIFY,
    
    # General API endpoints
    "/api/v1/*": settings.RATE_LIMIT_DEFAULT,
}

# IP whitelist (exempt from rate limiting)
IP_WHITELIST = {
    "127.0.0.1",  # localhost
    "::1",        # localhost IPv6
}

def is_whitelisted_ip(ip: str) -> bool:
    """
    Check if IP is whitelisted.
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if IP is whitelisted
    """
    return ip in IP_WHITELIST

def get_path_pattern(request: Request) -> Optional[str]:
    """
    Get the matching path pattern for rate limiting.
    
    Args:
        request: FastAPI request
        
    Returns:
        Optional[str]: Matching path pattern or None
    """
    return next(
        (pattern for pattern in RATE_LIMIT_RULES.keys() 
         if request.url.path.startswith(pattern.replace("*", ""))),
        None
    )

def add_rate_limit_headers(response: Response, limit: str, remaining: int, reset: int) -> None:
    """
    Add rate limit headers to response.
    
    Args:
        response: FastAPI response
        limit: Rate limit value
        remaining: Remaining requests
        reset: Reset timestamp
    """
    response.headers["X-RateLimit-Limit"] = limit
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset)

def setup_rate_limiting(app):
    """
    Configure rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    # Register rate limiter with app
    app.state.limiter = limiter
    
    # Add limiter exception handler
    from slowapi.errors import RateLimitExceeded
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        return Response(
            content='{"detail": "Too many requests"}',
            status_code=429,
            media_type="application/json"
        )
        
    # Register the HTTP middleware
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Skip rate limiting for whitelisted IPs
        client_ip = get_remote_address(request)
        if is_whitelisted_ip(client_ip):
            return await call_next(request)
        
        # Process request - rate limiting is handled by slowapi middleware
        response = await call_next(request)
        
        # Return response with or without rate limit headers
        return response 