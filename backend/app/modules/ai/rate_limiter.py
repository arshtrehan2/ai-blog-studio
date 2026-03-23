import time
from fastapi import HTTPException
from ...config import settings

# Module-level redis client (lazily initialized)
_redis_client = None


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        import redis
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def set_redis_client(client):
    """Allow injecting a mock client for testing."""
    global _redis_client
    _redis_client = client


def check_rate_limit(user_id: str) -> None:
    """
    Sliding window rate limiter using Redis sorted sets.
    Allows AI_RATE_LIMIT requests per user per AI_RATE_LIMIT_WINDOW seconds.
    """
    client = get_redis_client()
    key = f"user:{user_id}:ai"
    now = time.time()
    window_start = now - settings.AI_RATE_LIMIT_WINDOW

    pipe = client.pipeline()
    # Remove timestamps outside the current window
    pipe.zremrangebyscore(key, 0, window_start)
    # Count requests in the current window
    pipe.zcard(key)
    # Add current timestamp
    pipe.zadd(key, {str(now): now})
    # Set key expiry to the window duration
    pipe.expire(key, settings.AI_RATE_LIMIT_WINDOW)
    results = pipe.execute()

    current_count = results[1]

    if current_count >= settings.AI_RATE_LIMIT:
        # Calculate retry_after based on the oldest entry in the window
        oldest = client.zrange(key, 0, 0, withscores=True)
        if oldest:
            retry_after = int(settings.AI_RATE_LIMIT_WINDOW - (now - oldest[0][1]))
        else:
            retry_after = settings.AI_RATE_LIMIT_WINDOW
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(max(retry_after, 1))},
        )
