from tokenize import group
from pydantic import BaseModel, ConfigDict
from auth.schemas import Message, Chat
from typing import List


class Full_info_chat(BaseModel):
    messages: List[Message]
    chats: List[Chat]
    model_config = ConfigDict(from_attributes=True)


class Websocket_to_server_data(BaseModel):
    chat_id: int
    group_id: int
    message: str

    model_config = ConfigDict(from_attributes=True)

class Server_to_websocket_data(BaseModel):
    message: str
    name: str