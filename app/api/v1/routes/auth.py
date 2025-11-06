from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.core.supabase import get_supabase
from app.models.user import UserCreate, UserResponse
from app.models.common import SuccessResponse
from app.tasks.email_tasks import send_welcome_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    supabase: Client = Depends(get_supabase)
) -> SuccessResponse:
    """
    Register a new user.

    Args:
        user_data: User registration data
        supabase: Supabase client

    Returns:
        Success response with user data

    Raises:
        HTTPException: If registration fails
    """
    try:
        # Create user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        user = response.user

        # Send welcome email asynchronously
        send_welcome_email.delay(user.email, user.email.split("@")[0])

        return SuccessResponse(
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "created_at": user.created_at
                },
                "message": "User registered successfully. Please check your email for verification."
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=SuccessResponse)
async def login(
    user_data: UserCreate,
    supabase: Client = Depends(get_supabase)
) -> SuccessResponse:
    """
    Login user and get access token.

    Args:
        user_data: User login credentials
        supabase: Supabase client

    Returns:
        Success response with access token

    Raises:
        HTTPException: If login fails
    """
    try:
        # Sign in with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        return SuccessResponse(
            data={
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "token_type": "bearer",
                "expires_in": response.session.expires_in,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    supabase: Client = Depends(get_supabase),
    current_user: dict = Depends(get_supabase)
) -> SuccessResponse:
    """
    Logout current user.

    Args:
        supabase: Supabase client
        current_user: Current authenticated user

    Returns:
        Success response

    Raises:
        HTTPException: If logout fails
    """
    try:
        # Sign out from Supabase
        supabase.auth.sign_out()

        return SuccessResponse(
            data={"message": "Logged out successfully"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/refresh", response_model=SuccessResponse)
async def refresh_token(
    refresh_token: str,
    supabase: Client = Depends(get_supabase)
) -> SuccessResponse:
    """
    Refresh access token.

    Args:
        refresh_token: Refresh token
        supabase: Supabase client

    Returns:
        Success response with new access token

    Raises:
        HTTPException: If refresh fails
    """
    try:
        response = supabase.auth.refresh_session(refresh_token)

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        return SuccessResponse(
            data={
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "token_type": "bearer",
                "expires_in": response.session.expires_in
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )
