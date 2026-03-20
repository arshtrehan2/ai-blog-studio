"""Redis sliding-window rate limiter for AI endpoints."""
import time

import redis
from fastapi import HTTPException

from app.config import settings

_redis = redis.from_url(settings.REDIS_URL, decode_responses=True)


def check_rate_limit(user_id: str) -> None:
    """
    Sliding-window rate limiter using a Redis sorted set keyed by user_id.
    Raises HTTP 429 if the user has exceeded the configured limit.
    """
    key = f"user:{user_id}:ai"
    now = time.time()
    window_start = now - settings.AI_RATE_LIMIT_WINDOW_SECONDS

    pipe = _redis.pipeline()
    # Remove entries outside the current window
    pipe.zremrangebyscore(key, 0, window_start)
    # Add this request
    pipe.zadd(key, {str(now): now})
    # Count requests in the window
    pipe.zcard(key)
    # Reset the key TTL
    pipe.expire(key, settings.AI_RATE_LIMIT_WINDOW_SECONDS)
    results = pipe.execute()

    request_count: int = results[2]

    if request_count > settings.AI_RATE_LIMIT_REQUESTS:
        # Calculate Retry-After from the oldest entry in the window
        retry_after = settings.AI_RATE_LIMIT_WINDOW_SECONDS
        oldest = _redis.zrange(key, 0, 0, withscores=True)
        if oldest:
            oldest_ts = oldest[0][1]
            retry_after = int(oldest_ts + settings.AI_RATE_LIMIT_WINDOW_SECONDS - now)

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(max(retry_after, 1))},
        )
