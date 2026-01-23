from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse

from src.auth.config import settings
from src.auth.dependencies import DataFormDep, OAuth2PasswordRequestFormDep
from src.auth.services import authenticate_user, create_tokens, create_user
from src.database import SessionDep
from src.templates import templates

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/registration-page")
async def registration_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="auth/registration.html")


@router.post("/registration")
async def registration(data: DataFormDep, session: SessionDep) -> RedirectResponse:
    response = RedirectResponse(url="/users/me", status_code=status.HTTP_303_SEE_OTHER)
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
    return response


@router.get("/login-page")
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="auth/login.html")


@router.post("/login")
async def login(
    session: SessionDep, form_data: OAuth2PasswordRequestFormDep
) -> RedirectResponse:
    response = RedirectResponse(url="/users/me", status_code=status.HTTP_303_SEE_OTHER)
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
    return response


@router.get("/logout-page")
async def logout_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="auth/logout.html")


@router.post("/logout")
async def logout() -> RedirectResponse:
    response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access")
    response.delete_cookie(key="refresh")
    return response
