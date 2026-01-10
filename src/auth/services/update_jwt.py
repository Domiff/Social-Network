from fastapi import Request
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from src.auth.schemas import TokenPayload
from src.auth.services.user import create_access_jwt, get_user_by_id
from src.auth.utils import decode_jwt


async def update_access_jwt(request: Request, session: AsyncSession) -> str | bool:
    refresh = request.cookies.get("refresh")
    if not refresh:
        return False
    try:
        payload = decode_jwt(refresh)
        if payload["type"] != REFRESH_TOKEN_TYPE:
            return False
        user = await get_user_by_id(int(payload["sub"]), session)
        if not user:
            return False
        new_payload = TokenPayload(
            sub=str(user.id),
            type=ACCESS_TOKEN_TYPE,
        )
        access = create_access_jwt(new_payload)
        return access
    except (ExpiredSignatureError, InvalidTokenError):
        return False
