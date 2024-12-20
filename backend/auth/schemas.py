from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class JWTTokenSchema(BaseModel):
    access_token: str
    token_type: str

class TokenBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str

class TokenCreate(TokenBase):
    # token: str
    user: "UserDB"

class TokenRead(TokenBase):
    id: int
    # token: str
    user: "UserDB"

class TokenDB(TokenRead):
    # id: int
    # token: str
    # user: "UserDB
    pass


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: str

class UserCreate(UserBase):
    # name: str
    # email: str
    password: str

class UserRead(UserBase):
    id: int
    # name: str
    # email: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    token: Optional[List[TokenRead]] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserDB(UserRead):
    # id: int
    # name: str
    # email: str
    hashed_password: str
    # is_active: bool
    # is_verified: bool
    # is_superuser: bool
    # tokens: Optional[List[TokenRead]] = None
    
class Message(BaseModel):
    id: int
    local_id: int
    message: str
    user_id: int
    chat_id: int

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