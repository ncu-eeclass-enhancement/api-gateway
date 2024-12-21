from datetime import datetime
from pydantic import BaseModel, Field

from model.handout import Handout


class Course(BaseModel):
    id: int
    handouts: list[Handout] = Field(default_factory=list)
    vector_store_id: str | None = None
    assistant_id: str | None = None
    updated_time: datetime = Field(default_factory=datetime.now)
