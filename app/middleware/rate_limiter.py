import time
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis
from app.core.config import get_settings
from app.exceptions.base import RateLimitExceededException

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware.

    Limits requests per IP address using sliding window algorithm.
    """

    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            redis_client: Redis client instance
        """
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
        self.window_size = 60  # 60 seconds

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.

        Args:
            request: FastAPI request
            call_next: Next middleware/route handler

        Returns:
            Response or rate limit error
        """
        # Skip rate limiting for health check
        if request.url.path == f"{settings.API_V1_PREFIX}/health":
            return await call_next(request)

        # Skip if Redis is not available
        if not self.redis_client:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)
        rate_limit_key = f"rate_limit:{client_ip}"

        try:
            # Check rate limit
            current_time = int(time.time())
            window_start = current_time - self.window_size

            # Use Redis sorted set for sliding window
            pipe = self.redis_client.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(rate_limit_key, 0, window_start)

            # Count requests in current window
            pipe.zcard(rate_limit_key)

            # Add current request
            pipe.zadd(rate_limit_key, {str(current_time): current_time})

            # Set expiry
            pipe.expire(rate_limit_key, self.window_size)

            results = await pipe.execute()
            request_count = results[1]

            # Check if limit exceeded
            if request_count >= self.rate_limit:
                retry_after = self.window_size

                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Rate limit exceeded. "
                                      f"Retry after {retry_after} seconds",
                            "details": {"retry_after": retry_after}
                        }
                    },
                    headers={"Retry-After": str(retry_after)}
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, self.rate_limit - request_count - 1)
            )
            response.headers["X-RateLimit-Reset"] = str(
                current_time + self.window_size
            )

            return response

        except redis.RedisError as e:
            # If Redis fails, allow request but log error
            print(f"Rate limiter Redis error: {e}")
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Args:
            request: FastAPI request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (for proxies/load balancers)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return request.client.host if request.client else "unknown"
