from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from jwt import ExpiredSignatureError

from src.auth.config import settings
from src.auth.services import update_access_jwt
from src.auth.utils import decode_jwt
from src.database import async_session


async def access_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    access = request.cookies.get("access")
    refresh = request.cookies.get("refresh")
    if access:
        try:
            payload = decode_jwt(access)
            request.state.payload = payload
            return await call_next(request)
        except ExpiredSignatureError:
            pass
    if refresh:
        try:
            async with async_session() as session:
                new_access = await update_access_jwt(request, session)
            request.state.payload = decode_jwt(new_access)
            request.state.new_access = new_access
        except ExpiredSignatureError:
            return Response(status_code=401, content="You are need to be logged in")
    response = await call_next(request)
    if hasattr(request.state, "new_access") and request.url.path != "/auth/logout":
        response.set_cookie(
            "access",
            request.state.new_access,
            httponly=True,
            samesite="lax",
            max_age=settings.access_token_expire_minutes,
        )
    return response
