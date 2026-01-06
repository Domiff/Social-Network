from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class User(Base):
    username: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str] = mapped_column(String(75), unique=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_staff: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
