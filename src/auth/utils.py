import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from src.auth.config import settings


def encode_jwt(
    payload: dict,
    expires_minutes: int,
    algorithm: str = settings.algorithm,
) -> str:
    private_key: str = settings.private_key_path.read_text()
    data = payload.copy()
    now = datetime.now(tz=UTC)
    iat = now
    exp = iat + timedelta(minutes=expires_minutes)
    jti = str(uuid.uuid4())
    data.update({"iat": iat.timestamp(), "exp": exp.timestamp(), "jti": jti})
    encoded = jwt.encode(payload=data, key=private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    algorithm: str = settings.algorithm,
) -> dict:
    public_key: str = settings.public_key_path.read_text()
    decoded = jwt.decode(jwt=token, key=public_key, algorithms=[algorithm])
    return decoded


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    bytes_password = bcrypt.hashpw(password.encode(), salt)
    return bytes_password.decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
