from pydantic import BaseModel, Field


class Message(BaseModel):
    sender: int = Field(description="0: Assistant, 1: User")
    content: str
