import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import redis.asyncio as redis
from supabase import Client

from app.main import app
from app.core.redis import get_redis
from app.core.supabase import get_supabase
from app.services.cache_service import CacheService


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Mock Redis client for testing."""
    mock = AsyncMock(spec=redis.Redis)

    # Mock common Redis operations
    mock.get.return_value = None
    mock.set.return_value = True
    mock.setex.return_value = True
    mock.delete.return_value = 1
    mock.exists.return_value = False
    mock.ttl.return_value = -1
    mock.ping.return_value = True
    mock.scan.return_value = (0, [])

    return mock


@pytest.fixture
def mock_supabase() -> MagicMock:
    """Mock Supabase client for testing."""
    mock = MagicMock(spec=Client)

    # Mock auth operations
    mock.auth.sign_up.return_value = MagicMock(
        user=MagicMock(
            id="test-user-id",
            email="test@example.com",
            created_at="2024-01-01T00:00:00Z"
        )
    )

    mock.auth.sign_in_with_password.return_value = MagicMock(
        session=MagicMock(
            access_token="test-access-token",
            refresh_token="test-refresh-token",
            expires_in=3600
        ),
        user=MagicMock(
            id="test-user-id",
            email="test@example.com"
        )
    )

    mock.auth.get_user.return_value = MagicMock(
        user=MagicMock(
            id="test-user-id",
            email="test@example.com",
            created_at="2024-01-01T00:00:00Z",
            email_confirmed_at="2024-01-01T00:00:00Z"
        )
    )

    return mock


@pytest.fixture
def cache_service(mock_redis: AsyncMock) -> CacheService:
    """Cache service with mocked Redis."""
    return CacheService(mock_redis)


@pytest.fixture
def client(mock_redis: AsyncMock, mock_supabase: MagicMock) -> TestClient:
    """FastAPI test client with mocked dependencies."""

    async def override_get_redis():
        return mock_redis

    def override_get_supabase():
        return mock_supabase

    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_supabase] = override_get_supabase

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Authentication headers for testing protected endpoints."""
    return {
        "Authorization": "Bearer test-access-token"
    }


@pytest.fixture
def mock_user_data() -> dict:
    """Mock user data for testing."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "email_confirmed_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_post_data() -> dict:
    """Mock post data for testing."""
    return {
        "id": "test-post-id",
        "title": "Test Post",
        "content": "Test content",
        "published": True,
        "author_id": "test-user-id",
        "created_at": "2024-01-01T00:00:00Z"
    }


# Async test helpers
@pytest.fixture
async def async_mock_redis() -> AsyncGenerator[AsyncMock, None]:
    """Async mock Redis client."""
    mock = AsyncMock(spec=redis.Redis)
    mock.get.return_value = None
    mock.set.return_value = True
    mock.setex.return_value = True
    mock.delete.return_value = 1
    mock.exists.return_value = False
    mock.ttl.return_value = -1
    mock.ping.return_value = True
    mock.scan.return_value = (0, [])
    yield mock
