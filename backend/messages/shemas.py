from pydantic import BaseModel
from datetime import datetime

class MessageRead(BaseModel):
	id: int
	local_id: int
	text: str
	user_id: int
	chat_id: int
	created_at: datetime
