from pydantic import BaseModel, ConfigDict
from auth.schemas import MessageS, Chat
from typing import List, Tuple


class Full_info_chat(BaseModel):
    messages: List[MessageS]
    chats: List[Chat]
    model_config = ConfigDict(from_attributes=True)


class Websocket_to_server_data(BaseModel):
    chat_id: int
    group_id: int
    message: str

    model_config = ConfigDict(from_attributes=True)


class MessageServerToClient(BaseModel):
    message: MessageS
    author_id: int
    author_name: str


class AllLastMessages(BaseModel):
    group_id: int
    chat_id: int
    last_message_local_id: int | List[int]


class MessageUser(BaseModel):
    message: MessageS
    user_id: int
    user_name: str


class ChatMessages(BaseModel):
    group_id: int
    chat_id: int
    messages: List[Tuple[MessageS, int, str]]
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
