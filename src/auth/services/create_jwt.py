from src.auth.config import settings
from src.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE
from src.auth.schemas import TokenPayload
from src.auth.utils import encode_jwt


def create_jwt(
    token_type: str,
    token_data: dict,
    expires_minutes: int,
) -> str:
    jwt_payload = {TOKEN_TYPE: token_type}
    jwt_payload.update(token_data)
    token = encode_jwt(payload=jwt_payload, expires_minutes=expires_minutes)
    return token


def create_access_jwt(user: TokenPayload) -> str:
    payload = {"sub": user.sub}
    access = create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=payload,
        expires_minutes=settings.access_token_expire_minutes,
    )
    return access


def create_refresh_jwt(user: TokenPayload) -> str:
    payload = {"sub": user.sub}
    refresh = create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=payload,
        expires_minutes=settings.refresh_token_expire_minutes,
    )
    return refresh
