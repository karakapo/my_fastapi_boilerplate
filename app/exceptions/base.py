from typing import Optional, Any, Dict


class BaseAPIException(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base exception.

        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class UserNotFoundException(BaseAPIException):
    """Exception raised when user is not found."""

    def __init__(self, user_id: str):
        """
        Initialize user not found exception.

        Args:
            user_id: User ID that was not found
        """
        super().__init__(
            message=f"User with ID {user_id} not found",
            status_code=404,
            error_code="USER_NOT_FOUND",
            details={"user_id": user_id}
        )


class UnauthorizedException(BaseAPIException):
    """Exception raised when user is not authorized."""

    def __init__(self, message: str = "Unauthorized access"):
        """
        Initialize unauthorized exception.

        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )


class ResourceNotFoundException(BaseAPIException):
    """Exception raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        """
        Initialize resource not found exception.

        Args:
            resource_type: Type of resource
            resource_id: Resource ID
        """
        super().__init__(
            message=f"{resource_type} with ID {resource_id} not found",
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ValidationException(BaseAPIException):
    """Exception raised when validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize validation exception.

        Args:
            message: Error message
            details: Validation error details
        """
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class RateLimitExceededException(BaseAPIException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, retry_after: int):
        """
        Initialize rate limit exception.

        Args:
            retry_after: Seconds to wait before retrying
        """
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )
