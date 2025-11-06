from pydantic import BaseModel
from typing import Any, Optional, Dict


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    data: Any

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": {"message": "Operation completed successfully"}
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: Dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": {
                    "code": "ERROR_CODE",
                    "message": "Error description",
                    "details": {}
                }
            }
        }
    }


class PaginatedResponse(BaseModel):
    """Paginated response schema."""
    success: bool = True
    data: list
    page: int
    page_size: int
    total: Optional[int] = None
    has_next: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": [],
                "page": 1,
                "page_size": 20,
                "total": 100,
                "has_next": True
            }
        }
    }
