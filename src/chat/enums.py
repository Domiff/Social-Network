from enum import StrEnum


class ChatType(StrEnum):
    PRIVATE = "private"
    GROUP = "group"


class ChatRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
