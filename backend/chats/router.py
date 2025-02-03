from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from models import Chat, User
from dao import ChatManager, GroupManager, UserGroupManager
from database import get_async_session
from auth.utils import (
	get_token,
	get_current_active_user,
	my_list_permissions,
)
from auth.schemas import PermissionEnum


router = APIRouter(prefix='/api/chats', tags=['chats'])


@router.get('/{group_id}')
async def get_group_chats(
	group_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[AsyncSession, Depends(get_async_session)],
):
	await UserGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

	group = await GroupManager.get_one_by(session, id=group_id)
	chats = await GroupManager.get_chats(session, group=group)
	return chats


@router.post('/{group_id}')
async def create_group_chat(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	permissions: Annotated[str, Depends(my_list_permissions)],
	user: Annotated[User, Depends(get_current_active_user)],
	title: str,
	group_id: int,
):
	await UserGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

	if PermissionEnum.CAN_CREATE_CHAT.value not in permissions:
		raise HTTPException(status.HTTP_403_FORBIDDEN)

	group = await GroupManager.get_one_by(session, id=group_id)
	chat = Chat(title=title, group=group)
	await ChatManager.create(session, chat)
	await session.commit()
	return {'status': status.HTTP_201_CREATED}


@router.delete('/{group_id}/{chat_id}')
async def delete_group_chat(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	permissions: Annotated[str, Depends(my_list_permissions)],
	chat_id: int,
	group_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
):
	await UserGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

	if PermissionEnum.CAN_DELETE_CHAT.value not in permissions:
		return HTTPException(status.HTTP_403_FORBIDDEN)

	chat = await ChatManager.get_one_by(session, id=chat_id)
	await ChatManager.delete(session, chat)
	return {'status': status.HTTP_204_NO_CONTENT}
