from pydantic import BaseModel, ConfigDict
from auth.schemas import Message, Chat
from typing import List, Tuple


class Full_info_chat(BaseModel):
	messages: List[Message]
	chats: List[Chat]
	model_config = ConfigDict(from_attributes=True)


class Websocket_to_server_data(BaseModel):
	chat_id: int
	group_id: int
	message: str

	model_config = ConfigDict(from_attributes=True)


class Server_to_client(BaseModel):
	id: int
	local_id: int
	text: str
	name: str
	chat_id: int
	created_at: str


class AllLastMessages(BaseModel):
	group_id: int
	chat_id: int
	last_message_local_id: int | List[int]


class ChatMessages(BaseModel):
	group_id: int
	chat_id: int
	messages: List[Tuple[Message, str]]
	model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
