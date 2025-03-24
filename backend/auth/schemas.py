from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum
import datetime


class JWTTokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str


class TokenCreate(TokenBase):
    # token: str
    user: 'UsrDB'


class TokenRead(TokenBase):
    id: int
    # token: str
    user: 'UsrDB'


class TokenDB(TokenRead):
    # id: int
    # token: str
    # user: "UsrDB
    pass


class UsrBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    name_account: str


class UsrCreate(UsrBase):
    name: str
    email: str
    password: str


class UsrRead(UsrBase):
    id: int


class UsrUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UsrDB(UsrRead):
    # id: int
    # name: str
    email: str
    hashed_password: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    tokens: Optional[List[TokenRead]] = None


class BotUsrCreate(UsrBase):
    name: str
    password: str


class MessageS(BaseModel):
    id: int
    local_id: int
    text: str
    user_id: int
    chat_id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class Chat(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class GroupRead(BaseModel):
    id: int
    title: str
    description: str
    model_config = ConfigDict(from_attributes=True)


class ListGroupRead(BaseModel):
    groups: List[GroupRead]
    model_config = ConfigDict(from_attributes=True)


class PermissionEnum(Enum):
    ADMIN = 'admin'
    CAN_EDIT_ROLE = 'can_edit_role'
    CAN_CREATE_GROUP = 'can_create_group'
    CAN_EDIT_MAIN_INFO_GROUP = 'can_edit_main_info_group'
    CAN_CREATE_CHAT = 'can_create_chat'
    CAN_EDIT_CHAT = 'can_edit_chat'
    CAN_DELETE_CHAT = 'can_delete_chat'
