from enum import Enum

from pydantic import BaseModel


class Sender(Enum):
    SYSTEM = 0
    USER = 1


class Message(BaseModel):
    sender: Sender
    content: str


class History(BaseModel):
    history: list[Message]
