from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPBearer

from src.auth.exceptions import Unauthorized
from src.auth.jwt import JWT, get_jwt
from src.auth.repository import UserRepository, get_user_repo
from src.auth.schemas import UserSchema
from src.core.database import SessionDep

token_schema = HTTPBearer(auto_error=False)


def get_user_repo_dep(session: SessionDep) -> UserRepository:
    return get_user_repo(session)


TokenDep = Annotated[str, Security(token_schema)]
JWTDep = Annotated[JWT, Depends(get_jwt)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repo_dep)]


async def get_current_user(
    token: TokenDep,
    jwt: JWTDep,
    user_repo: UserRepositoryDep,
) -> UserSchema:
    payload = jwt.get_payload(token)
    if not payload:
        raise Unauthorized()
    user_id: str = payload.get("sub")
    user = await user_repo.get_by_id(int(user_id))
    return UserSchema.from_orm(user)
