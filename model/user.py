from pydantic import BaseModel, Field

from model.history import History


class User(BaseModel):
    id: str
    histories: list[History] = Field(default_factory=list)
