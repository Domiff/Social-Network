from fastapi import APIRouter, Response, Request

from src.auth.config import settings
from src.auth.dependencies import DataFormDep, OAuth2PasswordRequestFormDep
from src.auth.services import authenticate_user, create_tokens, create_user
from src.database import SessionDep
from src.templates import templates

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/registration-page")
async def registration_page(request: Request):
    return templates.TemplateResponse("auth/registration.html", {"request": request})


@router.post("/registration")
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


@router.get("/login-page")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


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


@router.get("/logout-page")
async def logout_page(request: Request):
    return templates.TemplateResponse("auth/logout.html", {"request": request})


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access")
    response.delete_cookie(key="refresh")
    return {"detail": "Logged out successfully"}
