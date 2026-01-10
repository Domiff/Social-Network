from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    type: Annotated[str, Literal["access", "refresh"]]


class User(BaseModel):
    id: int
    username: str
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None


class UserInDB(User):
    password: str
    is_staff: bool | None = None


class DataForm(BaseModel):
    username: str
    password: str
    email: EmailStr
