import pytest
from sqlalchemy.exc import NoResultFound

from src.auth.models import User
from tests.factories import make_credentials


@pytest.mark.parametrize(
    "credentials",
    [
        make_credentials(),
        make_credentials(),
        make_credentials(),
    ],
)
async def test_create_user(user_repo, credentials):
    user = await user_repo.create(credentials)

    assert user is not None
    assert isinstance(user, User)
    assert isinstance(user.username, str)


async def test_list(user_repo):
    credentials = make_credentials()
    await user_repo.create(credentials)

    users = await user_repo.list()

    assert users
    assert isinstance(users[0], User)
    assert isinstance(users, list)


async def test_get_user_by_email(user_repo):
    credentials = make_credentials()
    await user_repo.create(credentials)
    user = await user_repo.get_by_email(credentials["email"])

    assert user is not None
    assert isinstance(user, User)


async def test_get_user_by_id(user_repo):
    credentials = make_credentials()
    user = await user_repo.create(credentials)
    user = await user_repo.get_by_id(user.id)

    assert user is not None
    assert isinstance(user, User)


async def test_get_by_username(user_repo):
    credentials = make_credentials()
    user = await user_repo.create(credentials)
    user = await user_repo.get_by_username(user.username)

    assert user is not None
    assert isinstance(user, User)


async def test_update(user_repo):
    credentials = make_credentials()
    user = await user_repo.create(credentials)

    await user_repo.update(user.email, {"username": "New name"})

    assert user.username != credentials["username"]
    assert user.username == "New name"


async def test_delete(user_repo):
    """Test hard deleting a user, where is_soft = False in user_repo.delete"""

    credentials = make_credentials()
    user = await user_repo.create(credentials)

    await user_repo.delete(user.email, False)

    with pytest.raises(NoResultFound):
        await user_repo.get_by_email(user.email)
        await user_repo.get_by_id(user.id)
