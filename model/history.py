from pydantic import BaseModel, Field

from model.message import Message


class History(BaseModel):
    course_id: int
    history: list[Message] = Field(default_factory=list)
