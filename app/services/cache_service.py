import json
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()


class CacheService:
    """Redis cache service with JSON serialization."""

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize cache service.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.default_ttl = settings.DEFAULT_CACHE_TTL

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (json.JSONDecodeError, redis.RedisError) as e:
            print(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: DEFAULT_CACHE_TTL)

        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except (TypeError, redis.RedisError) as e:
            print(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            await self.redis.delete(key)
            return True
        except redis.RedisError as e:
            print(f"Cache delete error for key {key}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        try:
            cursor = 0
            deleted_count = 0
            while True:
                cursor, keys = await self.redis.scan(
                    cursor,
                    match=pattern,
                    count=100
                )
                if keys:
                    deleted_count += await self.redis.delete(*keys)
                if cursor == 0:
                    break
            return deleted_count
        except redis.RedisError as e:
            print(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        try:
            return await self.redis.exists(key) > 0
        except redis.RedisError:
            return False

    async def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.

        Args:
            key: Cache key

        Returns:
            Remaining TTL in seconds, -1 if no expiry, None if key doesn't exist
        """
        try:
            ttl = await self.redis.ttl(key)
            if ttl == -2:  # Key doesn't exist
                return None
            return ttl
        except redis.RedisError:
            return None
