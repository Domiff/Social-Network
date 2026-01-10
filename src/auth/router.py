from fastapi import APIRouter, Response

from src.auth.config import settings
from src.auth.dependencies import DataFormDep, OAuth2PasswordRequestFormDep
from src.auth.services import authenticate_user, create_tokens, create_user
from src.database import SessionDep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def registration(data: DataFormDep, session: SessionDep, response: Response):
    user = await create_user(data, session)
    tokens = create_tokens(user)
    response.set_cookie(
        key="access",
        value=tokens.access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes,
        # secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh",
        value=tokens.refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expire_minutes,
        # secure=True,
        samesite="strict",
    )
    return {"detail": "Registered in successfully"}


@router.post("/login")
async def login(
    session: SessionDep, form_data: OAuth2PasswordRequestFormDep, response: Response
):
    tokens = await authenticate_user(form_data.username, form_data.password, session)
    response.set_cookie(
        key="access",
        value=tokens.access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes,
        # secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh",
        value=tokens.refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expire_minutes,
        # secure=True,
        samesite="strict",
    )
    return {"detail": "Logged in successfully"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access")
    response.delete_cookie(key="refresh")
    return {"detail": "Logged out successfully"}
