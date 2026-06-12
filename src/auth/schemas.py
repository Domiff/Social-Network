from pydantic import EmailStr

from src.core.schemas import BaseSchema


class CredentialsSchema(BaseSchema):
    username: str | None = None
    password: str
    email: EmailStr
