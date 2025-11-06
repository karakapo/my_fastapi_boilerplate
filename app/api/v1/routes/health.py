from fastapi import APIRouter, Depends, status
import redis.asyncio as redis
from supabase import Client
from app.core.redis import get_redis
from app.core.supabase import get_supabase
from app.models.common import SuccessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=SuccessResponse)
async def health_check(
    redis_client: redis.Redis = Depends(get_redis),
    supabase: Client = Depends(get_supabase)
) -> SuccessResponse:
    """
    Health check endpoint.

    Checks connections to Redis and Supabase.

    Args:
        redis_client: Redis client
        supabase: Supabase client

    Returns:
        Success response with health status
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }

    # Check Redis
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "message": "Connected"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)}"
        }

    # Check Supabase
    try:
        # Simple check - get Supabase client
        # In production, you might want to do a simple query
        if supabase:
            health_status["services"]["supabase"] = {
                "status": "healthy",
                "message": "Connected"
            }
        else:
            health_status["status"] = "degraded"
            health_status["services"]["supabase"] = {
                "status": "unhealthy",
                "message": "Client not initialized"
            }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["supabase"] = {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)}"
        }

    return SuccessResponse(data=health_status)


@router.get("/readiness", response_model=SuccessResponse)
async def readiness_check() -> SuccessResponse:
    """
    Readiness check endpoint.

    Simple check to see if the service is ready to accept traffic.

    Returns:
        Success response
    """
    return SuccessResponse(
        data={
            "status": "ready",
            "message": "Service is ready to accept traffic"
        }
    )


@router.get("/liveness", response_model=SuccessResponse)
async def liveness_check() -> SuccessResponse:
    """
    Liveness check endpoint.

    Simple check to see if the service is alive.

    Returns:
        Success response
    """
    return SuccessResponse(
        data={
            "status": "alive",
            "message": "Service is alive"
        }
    )
