from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastcrud.types import GetMultiResponseModel
from sqlalchemy.exc import NoResultFound

from src.auth.depends import get_current_user
from src.chat.repositories import (
    ChatRepository,
    MessageRepository,
    get_chat_repository,
    get_message_repository,
)
from src.chat.schemas import ChatIn, ChatOut, MessageOut
from src.core.exceptions import DoesNotExists

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    dependencies=[Depends(get_current_user)],
)

ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: ChatIn,
    repo: ChatRepositoryDep,
) -> ChatOut:
    return await repo.create(data=data)


@router.get("")
async def list_chats(
    repo: ChatRepositoryDep,
) -> GetMultiResponseModel[ChatOut]:
    return await repo.list()


@router.get("/{chat_id}")
async def detail_chat(
    chat_id: int,
    repo: ChatRepositoryDep,
) -> ChatOut:
    chat = await repo.detail(chat_id=chat_id)
    if chat is None:
        raise DoesNotExists("Chat does not exist")
    return chat


@router.patch("/{chat_id}")
async def update_chat(
    chat_id: int,
    data: ChatIn,
    repo: ChatRepositoryDep,
) -> ChatOut | None:
    try:
        return await repo.update(chat_id=chat_id, data=data)
    except NoResultFound as e:
        raise DoesNotExists("Chat does not exist") from e


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    repo: ChatRepositoryDep,
) -> None:
    if not await repo.exists(chat_id=chat_id):
        raise DoesNotExists("Chat does not exist")
    await repo.delete(chat_id=chat_id)


@router.get("/{chat_id}/messages")
async def list_messages(
    chat_id: int,
    repo: MessageRepositoryDep,
) -> GetMultiResponseModel[MessageOut]:
    return await repo.list(chat_id=chat_id)
