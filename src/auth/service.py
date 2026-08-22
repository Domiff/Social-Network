from typing import Annotated

from fastapi import Depends, Response
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import Forbidden
from src.auth.jwt import get_jwt
from src.auth.repository import get_user_repo
from src.auth.schemas import CredentialsSchema, TokenOut
from src.auth.utils import get_password_hash, verify_password
from src.core.config import settings
from src.core.database import SessionDep
from src.core.exceptions import AlreadyExists, DoesNotExists
from src.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = get_user_repo(self.session)
        self.jwt = get_jwt()

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
        try:
            user = await self.repo.create(data)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error("User already exists", email=credentials.email)
            raise AlreadyExists() from e
        logger.info("User created successfully", user_id=user.id)
        return self._authenticate(user.id, response)

    async def login(
        self, credentials: CredentialsSchema, response: Response
    ) -> TokenOut:
        try:
            user = await self.repo.get_by_email(credentials.email)
        except NoResultFound as e:
            logger.error("User does not exist", email=credentials.email)
            raise DoesNotExists() from e
        if not verify_password(credentials.password, user.password):
            logger.error("Password mismatch", user_id=user.id)
            raise Forbidden("Password mismatch")
        logger.info("User logged in", user_id=user.id)
        return self._authenticate(user.id, response)

    async def logout(self, response: Response) -> None:
        self._remove_refresh_cookie(response)
        logger.info("User logged out")

    async def refresh(self, response: Response, refresh_token: str) -> TokenOut:
        self._remove_refresh_cookie(response)
        tokens = self.jwt.refresh_jwt(refresh_token)
        self._set_refresh_cookie(tokens.refresh_token, response)
        logger.info("Tokens refreshed")
        return TokenOut(access_token=tokens.access_token)


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
