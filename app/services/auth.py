from typing import Annotated

from fastapi import Depends

from app.core.exception import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.model.user import User
from app.repository.user import DepUserRepository, UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, data: RegisterRequest) -> User:
        if await self.user_repo.get_by_username(data.username):
            raise AppError(
                message="Username already taken",
                status_code=409,
                code="USERNAME_EXISTS",
            )

        if await self.user_repo.get_by_email(data.email):
            raise AppError(
                message="Email already registered",
                status_code=409,
                code="EMAIL_EXISTS",
            )

        user = User(
            full_name=data.full_name,
            username=data.username,
            phone_number=data.phone_number,
            email=data.email,
            password_hash=hash_password(data.password),
        )
        return await self.user_repo.create(user)

    async def login(self, username: str, password: str) -> str:
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise AppError(
                message="Invalid username or password",
                status_code=401,
                code="INVALID_CREDENTIALS",
            )

        return create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )


def get_auth_service(user_repo: DepUserRepository) -> AuthService:
    return AuthService(user_repo)


DepAuthService = Annotated[AuthService, Depends(get_auth_service)]
