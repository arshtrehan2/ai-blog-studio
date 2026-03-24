import time
from typing import Tuple
import redis.asyncio as aioredis
from app.config import settings


class RateLimiter:
    """Sliding window rate limiter using Redis sorted sets."""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.max_requests = settings.AI_RATE_LIMIT_REQUESTS
        self.window_seconds = settings.AI_RATE_LIMIT_WINDOW_SECONDS

    async def check(self, user_id: str) -> Tuple[bool, int]:
        """
        Check if the user is within rate limit.
        Returns (allowed: bool, retry_after_seconds: int)
        """
        key = f"user:{user_id}:ai_rate"
        now = time.time()
        window_start = now - self.window_seconds

        pipe = self.redis.pipeline()
        await pipe.zremrangebyscore(key, 0, window_start)
        await pipe.zcard(key)
        await pipe.zadd(key, {str(now): now})
        await pipe.expire(key, self.window_seconds)
        results = await pipe.execute()

        current_count = results[1]

        if current_count >= self.max_requests:
            await self.redis.zrem(key, str(now))
            oldest_entries = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest_entries:
                oldest_ts = oldest_entries[0][1]
                retry_after = int(oldest_ts + self.window_seconds - now) + 1
            else:
                retry_after = self.window_seconds
            return False, max(1, retry_after)

        return True, 0


_redis_client: aioredis.Redis = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def get_rate_limiter() -> RateLimiter:
    redis = await get_redis()
    return RateLimiter(redis)
