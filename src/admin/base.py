import time

from sqladmin import ModelView

from src.admin.mixins import RoleMixin


class BaseAdmin(ModelView):
    use_pretty_export = True
    page_size = 25

    def get_export_name(self, export_type: str) -> str:
        return f"{self.model.__name__.lower()}_{time.strftime('%Y-%m-%d_%H-%M')}.{export_type}"
