from app.core.response import success_response
from app.core.security import DepCurrentUser
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth import DepAuthService
from fastapi import APIRouter, status

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, auth_service: DepAuthService):
    user = await auth_service.register(data)
    return success_response(
        data=UserResponse(
            id=user.id,
            full_name=user.full_name,
            username=user.username,
            phone_number=user.phone_number,
            email=user.email,
        ).model_dump(),
        message="User registered successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/login")
async def login(data: LoginRequest, auth_service: DepAuthService):
    access_token = await auth_service.login(data.username, data.password)
    return success_response(
        data=TokenResponse(access_token=access_token).model_dump(),
        message="Login successful",
    )


@router.get("/me")
async def get_me(current_user: DepCurrentUser):
    return success_response(
        data=current_user,
        message="Current user retrieved",
    )
