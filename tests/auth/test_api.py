import pytest

from tests.factories import make_credentials
from tests.utils import get_refresh_token


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_registration(client, credentials):
    response = await client.post("/auth/register", json=credentials)

    assert response.status_code == 201
    assert response.cookies.get("refresh_token")


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_login(client, credentials):
    await client.post("/auth/register", json=credentials)

    response = await client.post("/auth/login", json=credentials)

    assert response.status_code == 200
    assert response.cookies.get("refresh_token")


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_logout(client, credentials):
    registration_response = await client.post("/auth/register", json=credentials)
    refresh_token = get_refresh_token(registration_response)

    response = await client.post("/auth/logout", json={"refresh_token": refresh_token})

    assert response.status_code == 204
