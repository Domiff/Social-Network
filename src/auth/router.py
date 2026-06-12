from fastapi import APIRouter, Response, Security, status
from fastapi.security import APIKeyCookie

from src.auth.schemas import CredentialsSchema
from src.auth.service import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["Auth"])
refresh_token_schema = APIKeyCookie(name="refresh_token", auto_error=True)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: CredentialsSchema, service: AuthServiceDep, response: Response
):
    return await service.register(data, response)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(data: CredentialsSchema, service: AuthServiceDep, response: Response):
    return await service.login(data, response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(service: AuthServiceDep, response: Response):
    await service.logout(response)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    service: AuthServiceDep,
    response: Response,
    refresh_token: str = Security(refresh_token_schema),
):
    return await service.refresh(response, refresh_token)
