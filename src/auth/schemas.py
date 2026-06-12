from pydantic import EmailStr

from src.core.schemas import BaseSchema


class CredentialsSchema(BaseSchema):
    username: str | None = None
    password: str
    email: EmailStr


class PairTokens(BaseSchema):
    access_token: str
    refresh_token: str


class TokenOut(BaseSchema):
    access_token: str
    token_type: str = "Bearer"
