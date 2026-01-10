from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from src.auth.exceptions import (
    incorrect_credentials,
    username_already_taken,
)
from src.auth.models import User
from src.auth.schemas import DataForm, Token, TokenPayload, UserInDB
from src.auth.services.create_jwt import create_access_jwt, create_refresh_jwt
from src.auth.utils import hash_password, verify_password
from src.database import SessionDep


async def create_user(user_data: DataForm, session: SessionDep) -> UserInDB:
    hashed_password = hash_password(user_data.password)
    try:
        user = User(
            username=user_data.username,
            password=hashed_password,
            email=user_data.email,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserInDB.model_validate(user, from_attributes=True)
    except IntegrityError as err:
        raise username_already_taken from err


def create_tokens(user: UserInDB) -> Token:
    access_token = create_access_jwt(
        TokenPayload(
            sub=str(user.id),
            type=ACCESS_TOKEN_TYPE,
        )
    )
    refresh_token = create_refresh_jwt(
        TokenPayload(
            sub=str(user.id),
            type=REFRESH_TOKEN_TYPE,
        )
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


async def get_user_by_username(username: str, session: SessionDep) -> User:
    query = select(User).where(User.username == username, User.is_active)
    user = await session.execute(query)
    return user.scalar_one_or_none()


async def get_user_by_id(_id: int, session: SessionDep) -> User:
    query = select(User).where(User.id == _id, User.is_active)
    user = await session.execute(query)
    return user.scalar_one_or_none()


async def authenticate_user(username: str, password: str, session: SessionDep) -> Token:
    user = await get_user_by_username(username, session)
    user_schema = UserInDB.model_validate(user, from_attributes=True)
    if verify_password(password, user.password):
        tokens = create_tokens(user_schema)
        return tokens
    else:
        raise incorrect_credentials


async def get_current_user(request: Request) -> UserInDB:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401)
    return user
