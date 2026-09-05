from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.auth.models import User
from src.chat.enums import ChatRole, ChatType
from src.core.database import Base


class Chat(Base):
    __tablename__ = "chats"

    type: Mapped[ChatType] = mapped_column(Enum(ChatType), default=ChatType.PRIVATE)
    name: Mapped[str] = mapped_column(String(100), nullable=True)

    members: Mapped[list[ChatMember]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    messages: Mapped[list[Message]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __str__(self) -> str:
        return self.name


class ChatMember(Base):
    __tablename__ = "chat_members"
    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_members_chat_user"),
    )

    role: Mapped[ChatRole] = mapped_column(Enum(ChatRole), default=ChatRole.MEMBER)

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    chat: Mapped[Chat] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="chat_members")
    messages: Mapped[list[Message]] = relationship(back_populates="sender")

    def __str__(self) -> str:
        return f"{self.user_id} in {self.chat_id}"


class Message(Base):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(String(3000), nullable=True)

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    sender_id: Mapped[int | None] = mapped_column(
        ForeignKey("chat_members.id", ondelete="SET NULL"), nullable=True, index=True
    )

    chat: Mapped[Chat] = relationship(back_populates="messages")
    sender: Mapped[ChatMember | None] = relationship(back_populates="messages")

    def __str__(self) -> str:
        return self.text if len(self.text) < 100 else self.text[:100] + "..."
