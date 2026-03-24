import time
import uuid
from typing import Optional

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def check_rate_limit(user_id: uuid.UUID, redis: Optional[aioredis.Redis] = None) -> tuple[bool, int]:
    """
    Sliding window rate limiter.
    Returns (is_allowed, retry_after_seconds).
    retry_after_seconds is 0 if allowed.
    """
    if redis is None:
        redis = get_redis()

    key = f"user:{user_id}:ai"
    now = time.time()
    window_start = now - settings.AI_RATE_LIMIT_WINDOW_SECONDS

    pipe = redis.pipeline()
    # Remove entries outside the window
    pipe.zremrangebyscore(key, "-inf", window_start)
    # Count current entries
    pipe.zcard(key)
    # Add current request with timestamp as score
    pipe.zadd(key, {str(now): now})
    # Set expiry
    pipe.expire(key, settings.AI_RATE_LIMIT_WINDOW_SECONDS)
    results = await pipe.execute()

    count = results[1]  # Count before adding current request
    if count >= settings.AI_RATE_LIMIT_REQUESTS:
        # Get the oldest entry to calculate retry_after
        oldest = await redis.zrange(key, 0, 0, withscores=True)
        if oldest:
            oldest_time = oldest[0][1]
            retry_after = int(oldest_time + settings.AI_RATE_LIMIT_WINDOW_SECONDS - now) + 1
        else:
            retry_after = settings.AI_RATE_LIMIT_WINDOW_SECONDS
        # Remove the entry we just added since we're rejecting
        await redis.zrem(key, str(now))
        return False, max(retry_after, 1)

    return True, 0
