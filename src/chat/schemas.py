from src.core.schemas import BaseSchema, DateTimeSchema


class MessageIn(BaseSchema):
    text: str | None = None
    chat_id: int | None = None


class MessageOut(BaseSchema, DateTimeSchema):
    id: int
    text: str
    chat_id: int


class ChatIn(BaseSchema):
    type: str | None = None
    name: str | None = None


class ChatOut(BaseSchema, DateTimeSchema):
    id: int
    type: str
    name: str | None = None
    messages: list[MessageOut] = []
