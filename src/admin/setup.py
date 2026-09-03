from fastapi import FastAPI, Request
from sqladmin import Admin
from sqladmin._menu import CategoryMenu

from src.admin.auth import AdminAuth

from src.core.config import settings
from src.core.database import new_session


def _category_is_visible(self: CategoryMenu, request: Request) -> bool:
    return any(
        child.is_visible(request) and child.is_accessible(request)
        for child in self.children
    )


def setup_admin(app: FastAPI) -> Admin:
    CategoryMenu.is_visible = _category_is_visible

    return Admin(
        app,
        session_maker=new_session,
        base_url="/admin",
        title="Social network admin",
        templates_dir="templates",
        authentication_backend=AdminAuth(secret_key=settings.admin.ADMIN_SECRET_KEY),
    )
