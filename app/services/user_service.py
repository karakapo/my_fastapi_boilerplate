from typing import Optional, Dict, Any
from supabase import Client
from app.models.user import UserResponse, UserUpdate
from app.services.cache_service import CacheService
from app.exceptions.base import UserNotFoundException


class UserService:
    """User service with caching."""

    def __init__(self, supabase: Client, cache: CacheService):
        """
        Initialize user service.

        Args:
            supabase: Supabase client
            cache: Cache service instance
        """
        self.supabase = supabase
        self.cache = cache

    def _get_user_cache_key(self, user_id: str) -> str:
        """Get cache key for user."""
        return f"user:{user_id}"

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """
        Get user by ID with caching.

        Args:
            user_id: User ID

        Returns:
            User data

        Raises:
            UserNotFoundException: If user not found
        """
        # Try cache first
        cache_key = self._get_user_cache_key(user_id)
        cached_user = await self.cache.get(cache_key)
        if cached_user:
            return UserResponse(**cached_user)

        # Cache miss - query database
        try:
            response = self.supabase.auth.admin.get_user_by_id(user_id)
            if not response.user:
                raise UserNotFoundException(user_id)

            user_data = {
                "id": response.user.id,
                "email": response.user.email,
                "created_at": response.user.created_at,
                "email_confirmed_at": response.user.email_confirmed_at
            }

            # Cache the result
            await self.cache.set(cache_key, user_data, ttl=3600)

            return UserResponse(**user_data)
        except Exception as e:
            if isinstance(e, UserNotFoundException):
                raise
            raise Exception(f"Failed to get user: {str(e)}")

    async def update_user(
        self,
        user_id: str,
        user_update: UserUpdate
    ) -> UserResponse:
        """
        Update user and invalidate cache.

        Args:
            user_id: User ID
            user_update: User update data

        Returns:
            Updated user data

        Raises:
            UserNotFoundException: If user not found
        """
        try:
            # Update in Supabase
            update_data = user_update.model_dump(exclude_unset=True)

            if "email" in update_data:
                await self.supabase.auth.admin.update_user_by_id(
                    user_id,
                    {"email": update_data["email"]}
                )

            if "password" in update_data:
                await self.supabase.auth.admin.update_user_by_id(
                    user_id,
                    {"password": update_data["password"]}
                )

            # Invalidate cache
            cache_key = self._get_user_cache_key(user_id)
            await self.cache.delete(cache_key)

            # Get fresh user data
            return await self.get_user_by_id(user_id)
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")

    async def invalidate_user_cache(self, user_id: str) -> None:
        """
        Invalidate all cache entries for a user.

        Args:
            user_id: User ID
        """
        cache_key = self._get_user_cache_key(user_id)
        await self.cache.delete(cache_key)
        # Also invalidate related patterns
        await self.cache.invalidate_pattern(f"user:{user_id}:*")
