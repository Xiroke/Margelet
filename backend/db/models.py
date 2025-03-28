from sqlalchemy import (
    BOOLEAN,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
    UniqueConstraint,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from db.database import Base
import datetime


class Permission(Base):
    __tablename__ = 'Permission'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(24), unique=True)

    roles: Mapped[List['Role']] = relationship(
        back_populates='permissions', secondary='RolePermission'
    )


class Role(Base):
    __tablename__ = 'Role'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(24))
    priority: Mapped[int] = mapped_column(Integer, autoincrement=True, default=1)
    # Best practice use array for postgresql, but i use sqlite for development
    permissions: Mapped[List['Permission']] = relationship(
        back_populates='roles', secondary='RolePermission', lazy='selectin'
    )
    group_id: Mapped[int] = mapped_column(ForeignKey('Group.id'), nullable=False)
    group: Mapped['Group'] = relationship(back_populates='roles')
    usergroups: Mapped[List['UsrGroup']] = relationship(
        back_populates='roles', secondary='RoleUsrGroup'
    )


class Usr(Base):
    __tablename__ = 'Usr'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(16))
    name_account: Mapped[str] = mapped_column(String(24), unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[Optional[str]] = mapped_column(String)
    panorama: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    tokens: Mapped[Optional[List['Token']]] = relationship(back_populates='user')
    groups: Mapped[Optional[List['Group']]] = relationship(
        back_populates='users', secondary='UsrGroup'
    )
    messages: Mapped[Optional[List['Message']]] = relationship(back_populates='user')
    readed_messages: Mapped[Optional[List['Message']]] = relationship(
        back_populates='who_readed', secondary='UsrReadedMessages'
    )

    def __repr__(self):
        return f'<{self.__class__.__name__, self.id, self.name, self.email}>'


class Token(Base):
    __tablename__ = 'Token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, default='No title')
    token: Mapped[str] = mapped_column(String, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Usr.id'), nullable=False)
    user: Mapped['Usr'] = relationship(back_populates='tokens')


class Chat(Base):
    __tablename__ = 'Chat'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    messages: Mapped[List['Message']] = relationship(back_populates='chat')

    group_id: Mapped[int] = mapped_column(ForeignKey('Group.id'), nullable=False)
    group: Mapped['Group'] = relationship(back_populates='chats')


class Message(Base):
    __tablename__ = 'Message'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    local_id: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(ForeignKey('Usr.id'), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey('Chat.id'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped['Usr'] = relationship(back_populates='messages')
    who_readed: Mapped['Usr'] = relationship(
        back_populates='readed_messages', secondary='UsrReadedMessages'
    )
    chat: Mapped['Chat'] = relationship(back_populates='messages')

    __table_args__ = (
        UniqueConstraint('chat_id', 'local_id', name='unique_chat_local_id'),
    )


class Group(Base):
    __tablename__ = 'Group'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(String(length=300))
    is_personal_group: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    panorama: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    users: Mapped[List['Usr']] = relationship(
        back_populates='groups', secondary='UsrGroup'
    )
    chats: Mapped[List['Chat']] = relationship(back_populates='group', lazy='subquery')
    roles: Mapped[List['Role']] = relationship(back_populates='group')


class UsrGroup(Base):
    __tablename__ = 'UsrGroup'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Usr.id'), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('Group.id'), nullable=False)
    roles: Mapped[List['Role']] = relationship(
        back_populates='usergroups', lazy='selectin', secondary='RoleUsrGroup'
    )


class RolePermission(Base):
    __tablename__ = 'RolePermission'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('Role.id'), nullable=False)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey('Permission.id'), nullable=False
    )


class RoleUsrGroup(Base):
    __tablename__ = 'RoleUsrGroup'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('Role.id'), nullable=False)
    usergroup_id: Mapped[int] = mapped_column(ForeignKey('UsrGroup.id'), nullable=False)


class UsrReadedMessages(Base):
    __tablename__ = 'UsrReadedMessages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('Usr.id'), nullable=False)
    message_id: Mapped[int] = mapped_column(ForeignKey('Message.id'), nullable=False)
