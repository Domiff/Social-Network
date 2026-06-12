import uuid
from datetime import datetime, timedelta
from typing import Literal

import jwt

from src.auth.exceptions import Forbidden, Unauthorized
from src.auth.schemas import PairTokens
from src.core.config import settings
from src.core.logging import get_logger

TokenType = Literal["access", "refresh"]
logger = get_logger(__name__)


class JWT:
    def _make_payload(self, sub: int, token_type: TokenType) -> dict:
        now = datetime.now()
        exp = now + (
            timedelta(hours=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
            if token_type == "access"
            else timedelta(hours=settings.auth.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return {
            "sub": str(sub),
            "exp": int(exp.timestamp()),
            "jti": uuid.uuid4().hex,
            "token_type": token_type,
        }

    def _encode_token(self, sub: int, token_type: TokenType) -> str:
        encoded = jwt.encode(
            payload=self._make_payload(sub, token_type),
            key=settings.auth.PRIVATE_KEY_PATH.read_text(),
            algorithm=settings.auth.ALGORITHM,
        )
        return encoded

    def _decode_token(self, token: str) -> dict:
        if not token:
            logger.warning("Token not found")
            raise Unauthorized("Token not found")
        try:
            payload = jwt.decode(
                token,
                settings.auth.PUBLIC_KEY_PATH.read_text(),
                algorithms=[settings.auth.ALGORITHM],
            )
        except jwt.ExpiredSignatureError as e:
            logger.warning("Token expired", err=str(e))
            raise Unauthorized("Token expired") from e
        except jwt.PyJWTError as e:
            logger.warning("Invalid token", err=str(e))
            raise Forbidden("Invalid token") from e
        logger.info("Token decoded")
        return payload

    def create_jwt(self, sub: int) -> PairTokens:
        access_token = self._encode_token(sub, "access")
        refresh_token = self._encode_token(sub, "refresh")
        return PairTokens(access_token=access_token, refresh_token=refresh_token)

    def refresh_jwt(self, token: str) -> PairTokens:
        payload = self._decode_token(token)
        access_token = self._encode_token(payload["sub"], "access")
        refresh_token = self._encode_token(payload["sub"], "refresh")
        return PairTokens(access_token=access_token, refresh_token=refresh_token)
