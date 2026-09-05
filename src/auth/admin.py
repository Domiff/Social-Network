from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import action, Flash
from sqladmin.filters import BooleanFilter

from src.admin.base import BaseAdmin
from src.auth.models import User
from src.auth.repository import get_user_repo
from src.core.database import new_session
from src.core.security import hash_password


class UserAdmin(BaseAdmin, model=User):
    # TODO: add roles to user model in future
    # allowed_roles =
    # write_roles =

    column_list = [
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.is_active,
    ]
    column_details_list = [
        User.id,
        User.username,
        User.email,
        User.password,
        User.first_name,
        User.last_name,
        User.is_active,
        User.created_at,
        User.updated_at,
    ]
    column_labels = {
        User.id: "Уникальный идентификатор",
        User.username: "Имя пользователя",
        User.password: "Пароль",
        User.email: "Email",
        User.first_name: "Имя",
        User.last_name: "Фамилия",
        User.is_active: "Статус",
        User.created_at: "Дата создания",
        User.updated_at: "Дата обновления",
    }
    column_searchable_list = [User.username, User.email, User.first_name, User.last_name]
    column_sortable_list = [
        User.username,
        User.email,
        User.first_name,
        User.last_name,
        User.is_active,
        User.created_at,
        User.updated_at,
    ]
    column_filters = [
        BooleanFilter(User.is_active, title="Статус"),
    ]

    form_create_rules = [
        "username",
        "password",
        "email",
        "first_name",
        "last_name",
    ]
    form_edit_rules = form_create_rules + ["is_active"]

    icon = "fa-solid fa-user-shield"
    category = "Доступ"
    category_icon = "fa-solid fa-lock"

    name = "Пользователь"
    name_plural = "Пользователи"

    async def on_model_change(
            self, data: dict, model: User, is_created: bool, request: Request
    ) -> None:
        password = data.pop("password")
        data["password"] = hash_password(password)

    @action(
        name="change_status",
        label="Change status",
        confirmation_message="Are you sure?",
    )
    async def change_status(self, request: Request):
        pks = request.query_params.get("pks", "").split(",")

        if not pks:
            pass

        async with new_session() as session:
            user_repo = get_user_repo(session)
            for pk in pks:
                user = await user_repo.get_by_id(int(pk))
                await user_repo.update(user.email, {"is_active": not bool(user.is_active)})

        Flash.success(request, "Statuses changed successfully")

        return RedirectResponse(request.url_for("admin:list", identity=self.identity))
