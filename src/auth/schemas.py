from pydantic import BaseModel, EmailStr


class CredentialsSchema(BaseModel):
    username: str | None = None
    password: str
    email: EmailStr
