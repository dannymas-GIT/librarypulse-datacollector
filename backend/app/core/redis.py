from redis import Redis
from app.core.config import settings

def get_redis() -> Redis:
    """
    Get Redis connection.
    
    Returns:
        Redis: Redis connection instance
    """
    return Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_timeout=5,
        retry_on_timeout=True
    ) 