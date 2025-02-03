from pydantic import BaseModel, ConfigDict


class ChatRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	title: str
	group_id: int
