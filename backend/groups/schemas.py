from pydantic import BaseModel, ConfigDict
from chats.schemas import ChatRead
from typing import List
import datetime


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    is_personal_group: bool
    created_at: datetime.datetime
    chats: List[ChatRead] | None


class GroupCreate(BaseModel):
    title: str
    description: str
