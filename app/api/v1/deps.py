from typing import AsyncGenerator
from fastapi import Depends
import redis.asyncio as redis
from supabase import Client
from app.core.redis import get_redis
from app.core.supabase import get_supabase
from app.core.security import get_current_user as _get_current_user
from app.services.cache_service import CacheService
from app.services.user_service import UserService


async def get_current_user(
    user: dict = Depends(_get_current_user)
) -> dict:
    """
    Get current authenticated user dependency.

    Args:
        user: User data from security dependency

    Returns:
        User data
    """
    return user


async def get_cache_service(
    redis_client: redis.Redis = Depends(get_redis)
) -> CacheService:
    """
    Get cache service dependency.

    Args:
        redis_client: Redis client

    Returns:
        Cache service instance
    """
    return CacheService(redis_client)


async def get_user_service(
    supabase: Client = Depends(get_supabase),
    cache: CacheService = Depends(get_cache_service)
) -> UserService:
    """
    Get user service dependency.

    Args:
        supabase: Supabase client
        cache: Cache service

    Returns:
        User service instance
    """
    return UserService(supabase, cache)
