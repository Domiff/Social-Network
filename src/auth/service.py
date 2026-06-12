from typing import Annotated

from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import Forbidden
from src.auth.jwt import JWT
from src.auth.repository import UserRepository
from src.auth.schemas import CredentialsSchema, TokenOut
from src.auth.utils import get_password_hash, verify_password
from src.core.config import settings
from src.core.database import SessionDep
from src.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(self.session)
        self.jwt = JWT()

    def _set_refresh_cookie(self, token: str, response: Response) -> None:
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            samesite="strict",
            secure=True,
            max_age=60 * 60 * 24 * settings.auth.REFRESH_TOKEN_EXPIRE_DAYS,
        )

    def _remove_refresh_cookie(self, response: Response) -> None:
        response.delete_cookie(key="refresh_token")

    def _authenticate(self, user_id: int, response: Response) -> TokenOut:
        tokens = self.jwt.create_jwt(user_id)
        self._set_refresh_cookie(tokens.refresh_token, response)
        return TokenOut(access_token=tokens.access_token)

    async def register(
        self, credentials: CredentialsSchema, response: Response
    ) -> TokenOut:
        data = {
            "username": credentials.username,
            "email": credentials.email,
            "password": get_password_hash(credentials.password),
        }
        user = await self.repo.create(data)
        return self._authenticate(user.id, response)

    async def login(
        self, credentials: CredentialsSchema, response: Response
    ) -> TokenOut:
        user = await self.repo.get_by_email(credentials.email)
        if not verify_password(credentials.password, user.password):
            raise Forbidden("Password mismatch")
        return self._authenticate(user.id, response)

    async def logout(self, response: Response) -> None:
        self._remove_refresh_cookie(response)

    async def refresh(self, response: Response, refresh_token: str) -> TokenOut:
        self._remove_refresh_cookie(response)
        tokens = self.jwt.refresh_jwt(refresh_token)
        self._set_refresh_cookie(tokens.refresh_token, response)
        return TokenOut(access_token=tokens.access_token)


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
