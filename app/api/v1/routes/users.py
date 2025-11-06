from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_current_user, get_user_service
from app.models.user import UserResponse, UserUpdate
from app.models.common import SuccessResponse
from app.services.user_service import UserService
from app.exceptions.base import UserNotFoundException

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=SuccessResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> SuccessResponse:
    """
    Get current user information.

    This endpoint uses caching for improved performance.

    Args:
        current_user: Current authenticated user
        user_service: User service

    Returns:
        Success response with user data

    Raises:
        HTTPException: If user not found
    """
    try:
        user_id = current_user.get("id")
        user = await user_service.get_user_by_id(user_id)

        return SuccessResponse(
            data=user.model_dump()
        )

    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


@router.get("/{user_id}", response_model=SuccessResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> SuccessResponse:
    """
    Get user by ID.

    This endpoint uses caching for improved performance.

    Args:
        user_id: User ID to fetch
        current_user: Current authenticated user
        user_service: User service

    Returns:
        Success response with user data

    Raises:
        HTTPException: If user not found
    """
    try:
        user = await user_service.get_user_by_id(user_id)

        return SuccessResponse(
            data=user.model_dump()
        )

    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


@router.put("/{user_id}", response_model=SuccessResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> SuccessResponse:
    """
    Update user information.

    This endpoint invalidates the user cache after update.

    Args:
        user_id: User ID to update
        user_update: User update data
        current_user: Current authenticated user
        user_service: User service

    Returns:
        Success response with updated user data

    Raises:
        HTTPException: If update fails or user not authorized
    """
    # Check if user is updating their own profile
    if user_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )

    try:
        updated_user = await user_service.update_user(user_id, user_update)

        return SuccessResponse(
            data={
                "user": updated_user.model_dump(),
                "message": "User updated successfully"
            }
        )

    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )
