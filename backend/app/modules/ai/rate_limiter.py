"""Redis sliding-window rate limiter for AI endpoints."""
import time
from typing import Optional

from fastapi import HTTPException, status

from app.config import get_settings

settings = get_settings()

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        import redis as redis_lib
        _redis_client = redis_lib.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def check_ai_rate_limit(user_id: str) -> None:
    """
    Sliding window rate limiter using Redis sorted sets.
    Raises HTTP 429 if the user has exceeded the limit.
    """
    r = _get_redis()
    key = f"user:{user_id}:ai"
    now = time.time()
    window_start = now - settings.ai_rate_limit_window_seconds

    pipe = r.pipeline()
    # Remove old entries
    pipe.zremrangebyscore(key, "-inf", window_start)
    # Count requests in window
    pipe.zcard(key)
    # Add current request
    pipe.zadd(key, {str(now): now})
    # Set TTL
    pipe.expire(key, settings.ai_rate_limit_window_seconds)
    results = pipe.execute()

    count = results[1]  # count BEFORE adding current request
    if count >= settings.ai_rate_limit_requests:
        # Calculate retry-after
        oldest = r.zrange(key, 0, 0, withscores=True)
        retry_after = 0
        if oldest:
            oldest_ts = oldest[0][1]
            retry_after = int(
                oldest_ts + settings.ai_rate_limit_window_seconds - now
            )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(max(0, retry_after))},
        )
