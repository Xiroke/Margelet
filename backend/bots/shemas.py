from pydantic import BaseModel


class BotWebsocketReceived(BaseModel):
	text: str
	chat_id: int
