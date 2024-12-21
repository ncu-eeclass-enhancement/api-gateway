from datetime import datetime

from pydantic import BaseModel, Field


class Handout(BaseModel):
    id: int | None = None
    filename: str
    content: bytes
    updated_time: datetime = Field(default_factory=datetime.now)
