import pytest
from fastapi import Response
from pwdlib import PasswordHash

from src.auth.schemas import CredentialsSchema, TokenOut
from tests.factories import make_credentials
from tests.utils import get_refresh_token


def hash_pwd(password):
    password_hash = PasswordHash.recommended()
    return password_hash.hash(password)


@pytest.fixture
def response():
    return Response()


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_register(auth_service, credentials, response):
    result = await auth_service.register(CredentialsSchema(**credentials), response)

    assert result
    assert isinstance(result, TokenOut)
    assert result.token_type == "Bearer"


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_login(user_repo, auth_service, credentials, response):
    create_data = {
        "username": credentials["username"],
        "password": hash_pwd(credentials["password"]),
        "email": credentials["email"],
    }
    await user_repo.create(create_data)

    result = await auth_service.login(CredentialsSchema(**credentials), response)

    assert result
    assert isinstance(result, TokenOut)
    assert result.token_type == "Bearer"


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_logout(user_repo, auth_service, credentials, response):
    create_data = {
        "username": credentials["username"],
        "password": hash_pwd(credentials["password"]),
        "email": credentials["email"],
    }
    await user_repo.create(create_data)
    await auth_service.login(CredentialsSchema(**credentials), response)

    result = await auth_service.logout(response)

    assert result is None


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_refresh(auth_service, credentials, response):
    await auth_service.register(CredentialsSchema(**credentials), response)
    refresh_token = get_refresh_token(response)

    result = await auth_service.refresh(response, refresh_token)

    assert result
    assert isinstance(result, TokenOut)
    assert result.token_type == "Bearer"
