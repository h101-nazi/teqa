import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def signup(self, data: SignupRequest) -> TokenResponse:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        user = await self.repo.create(user)

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        user = await self.repo.get_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token = create_access_token(str(user.id))
        new_refresh = create_refresh_token(str(user.id))

        return TokenResponse(access_token=access_token, refresh_token=new_refresh)

    async def get_current_user(self, token: str) -> User:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise ValueError("Invalid token")

        user_id = payload.get("sub")
        user = await self.repo.get_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        return user
