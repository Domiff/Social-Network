from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.chat.enums import ChatType
from src.core.database import Base


class Chat(Base):
    __tablename__ = "chats"

    type: Mapped[ChatType] = mapped_column(Enum(ChatType), default=ChatType.PRIVATE)
    name: Mapped[str] = mapped_column(String(100), nullable=True)

    messages: Mapped[list[Message]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __str__(self) -> str:
        return self.name


class Message(Base):
    __tablename__ = "messages"

    text: Mapped[str] = mapped_column(String(3000), nullable=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )

    chat: Mapped[Chat] = relationship(back_populates="messages")

    def __str__(self) -> str:
        return self.text if len(self.text) < 100 else self.text[100] + "..."
