from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    created_at: datetime
    email_confirmed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2024-01-01T00:00:00Z",
                "email_confirmed_at": "2024-01-01T00:00:00Z"
            }
        }
    }


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newemail@example.com"
            }
        }
    }
