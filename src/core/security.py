from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

def hash_password(password: str | bytes) -> str:
    return password_hash.hash(password)


def check_password(password: str | bytes, hashed_password: str | bytes) -> bool:
    return password_hash.verify(password, hashed_password)
