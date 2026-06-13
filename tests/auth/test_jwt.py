import pytest

from src.auth.jwt import get_jwt
from src.auth.schemas import PairTokens
from tests.factories import make_sub


@pytest.fixture
def jwt():
    return get_jwt()


@pytest.mark.parametrize("sub", [make_sub(), make_sub(), make_sub()])
def test_create_jwt(jwt, sub):
    tokens = jwt.create_jwt(sub)

    assert isinstance(tokens, PairTokens)
    assert isinstance(tokens.access_token, str)
    assert isinstance(tokens.refresh_token, str)


@pytest.mark.parametrize("sub", [make_sub(), make_sub(), make_sub()])
def test_refresh_jwt(jwt, sub):
    tokens = jwt.create_jwt(sub)

    refreshed_tokens = jwt.refresh_jwt(tokens.refresh_token)

    assert isinstance(refreshed_tokens, PairTokens)
    assert isinstance(refreshed_tokens.access_token, str)
    assert isinstance(refreshed_tokens.refresh_token, str)


@pytest.mark.parametrize("sub", [make_sub(), make_sub(), make_sub()])
def test_get_payload(jwt, sub):
    tokens = jwt.create_jwt(sub)

    payload = jwt.get_payload(tokens.refresh_token)

    assert isinstance(payload, dict)
    assert isinstance(payload["sub"], str)
    assert isinstance(payload["exp"], int)
    assert payload["exp"] > 0
    assert payload["sub"] == str(sub)
