from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from app.api.v1.deps import get_current_user, get_cache_service
from app.models.common import SuccessResponse, PaginatedResponse
from app.services.cache_service import CacheService
from app.tasks.email_tasks import send_notification_email

router = APIRouter(prefix="/posts", tags=["Posts"])


class PostCreate(BaseModel):
    """Post creation schema."""
    title: str
    content: str
    published: bool = False


class PostResponse(BaseModel):
    """Post response schema."""
    id: str
    title: str
    content: str
    published: bool
    author_id: str
    created_at: str


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    published_only: bool = Query(True),
    cache: CacheService = Depends(get_cache_service)
) -> PaginatedResponse:
    """
    List posts with pagination.

    This endpoint uses caching for improved performance.

    Args:
        page: Page number
        page_size: Items per page
        published_only: Filter for published posts only
        cache: Cache service

    Returns:
        Paginated response with posts
    """
    try:
        # Try cache first
        cache_key = f"posts:page:{page}:size:{page_size}:published:{published_only}"
        cached_posts = await cache.get(cache_key)

        if cached_posts:
            return PaginatedResponse(**cached_posts)

        # Cache miss - simulate database query
        # In real implementation, query Supabase database
        mock_posts = [
            {
                "id": f"post-{i}",
                "title": f"Post {i}",
                "content": f"Content for post {i}",
                "published": True,
                "author_id": "user-1",
                "created_at": "2024-01-01T00:00:00Z"
            }
            for i in range((page - 1) * page_size + 1, page * page_size + 1)
        ]

        result = {
            "success": True,
            "data": mock_posts,
            "page": page,
            "page_size": page_size,
            "total": 100,
            "has_next": page * page_size < 100
        }

        # Cache the result (30 minutes TTL for posts)
        await cache.set(cache_key, result, ttl=1800)

        return PaginatedResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list posts: {str(e)}"
        )


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user),
    cache: CacheService = Depends(get_cache_service)
) -> SuccessResponse:
    """
    Create a new post.

    Sends notification email in background.

    Args:
        post_data: Post creation data
        current_user: Current authenticated user
        cache: Cache service

    Returns:
        Success response with created post
    """
    try:
        # Simulate post creation
        # In real implementation, create in Supabase database
        new_post = {
            "id": "new-post-id",
            "title": post_data.title,
            "content": post_data.content,
            "published": post_data.published,
            "author_id": current_user.get("id"),
            "created_at": "2024-01-01T00:00:00Z"
        }

        # Invalidate posts cache
        await cache.invalidate_pattern("posts:*")

        # Send notification email asynchronously (if published)
        if post_data.published:
            user_email = current_user.get("email")
            send_notification_email.delay(
                user_email,
                "Post Published",
                f"Your post '{post_data.title}' has been published successfully!"
            )

        return SuccessResponse(
            data={
                "post": new_post,
                "message": "Post created successfully"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@router.get("/{post_id}", response_model=SuccessResponse)
async def get_post(
    post_id: str,
    cache: CacheService = Depends(get_cache_service)
) -> SuccessResponse:
    """
    Get post by ID.

    This endpoint uses caching for improved performance.

    Args:
        post_id: Post ID
        cache: Cache service

    Returns:
        Success response with post data

    Raises:
        HTTPException: If post not found
    """
    try:
        # Try cache first
        cache_key = f"post:{post_id}"
        cached_post = await cache.get(cache_key)

        if cached_post:
            return SuccessResponse(data=cached_post)

        # Cache miss - simulate database query
        # In real implementation, query Supabase database
        post = {
            "id": post_id,
            "title": f"Post {post_id}",
            "content": f"Content for post {post_id}",
            "published": True,
            "author_id": "user-1",
            "created_at": "2024-01-01T00:00:00Z"
        }

        # Cache the result (30 minutes TTL)
        await cache.set(cache_key, post, ttl=1800)

        return SuccessResponse(data=post)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get post: {str(e)}"
        )


@router.delete("/{post_id}", response_model=SuccessResponse)
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    cache: CacheService = Depends(get_cache_service)
) -> SuccessResponse:
    """
    Delete post by ID.

    Invalidates cache after deletion.

    Args:
        post_id: Post ID
        current_user: Current authenticated user
        cache: Cache service

    Returns:
        Success response

    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Simulate post deletion
        # In real implementation, delete from Supabase database

        # Invalidate cache
        await cache.delete(f"post:{post_id}")
        await cache.invalidate_pattern("posts:*")

        return SuccessResponse(
            data={"message": "Post deleted successfully"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {str(e)}"
        )
