from fastapi import Request
from pwdlib.exceptions import UnknownHashError
from sqladmin.authentication import AuthenticationBackend

from src.core.security import check_password

from src.auth.models import User
from src.auth.repository import get_user_repo
from src.core.database import new_session


class AdminAuth(AuthenticationBackend):
    @staticmethod
    async def _get_account(username: str) -> User | None:
        if not username:
            return None

        async with new_session() as session:
            return await get_user_repo(session).get_by_username(username)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))

        account = await self._get_account(username)

        if account is None or not account.is_active:
            return False

        try:
            is_valid = check_password(password, account.password)
        except UnknownHashError:
            return False

        if not is_valid:
            return False

        request.session.update({"user": account.username})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        account = await self._get_account(request.session.get("user", ""))
        return bool(account and account.is_active)
