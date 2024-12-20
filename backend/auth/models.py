from sqlalchemy import Integer, String, Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from database import Base


class User(Base):
    __tablename__ = 'User'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(18))
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[Optional[str]] = mapped_column(String)

    tokens: Mapped[Optional[List["Token"]]] = relationship(back_populates="user")
    groups: Mapped[Optional[List["Group"]]] = relationship("Group", back_populates="users", secondary="UserGroup")
    messages: Mapped[Optional[List["Message"]]] = relationship(back_populates="user")

class Token(Base):
    __tablename__ = 'Token'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, default="No title")
    token: Mapped[str] = mapped_column(String, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="tokens")

class Group(Base):
    __tablename__ = 'Group'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(Text(length=300))
    users: Mapped[List["User"]] = relationship("User", back_populates="groups", secondary="UserGroup")
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="group")

    
class Chat(Base):
    __tablename__ = 'Chat'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    messages: Mapped[List["Message"]] = relationship(back_populates="chat")

    group_id: Mapped[int] = mapped_column(ForeignKey("Group.id"), nullable=False)
    group: Mapped["Group"] = relationship("Group", back_populates="chats")
    
class UserGroup(Base):
    __tablename__ = 'UserGroup'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("Group.id"), nullable=False)

class Message(Base):
    __tablename__ = 'Message'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    local_id: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("Chat.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="messages")
    chat: Mapped["Chat"] = relationship(back_populates="messages")

    __table_args__ = (
        UniqueConstraint('local_id', 'chat_id', name='unique_local_id_per_chat'),
    )