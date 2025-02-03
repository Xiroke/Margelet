from fastapi import APIRouter, Depends, HTTPException, status
from models import Group, Usr, Chat
from dao import UsrManager, GroupManager, ChatManager
from database import get_async_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from auth.schemas import UsrRead
from typing import List
from fastapi import UploadFile
import datetime
from shutil import copyfileobj
import os
from auth.utils import get_current_active_user

router = APIRouter(prefix='/api/users', tags=['users'])

@router.get('/{field}')
async def search_users(
	session: Annotated[AsyncSession, Depends(get_async_session)], field: str
) -> List[UsrRead]:
	return await UsrManager.search_users(session, field)


@router.post('/add_friend/{friend_id}')
async def add_friend(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	user: Annotated[Usr, Depends(get_current_active_user)],
	friend_id: int,
):
	friend = await UsrManager.get_one_by(session, id=friend_id)

	if user.id == friend_id:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="You can't add yourself as a friend",
		)

	group = Group(
		title=f'{user.name_account}|{friend.name_account}:{user.id}|{friend.id}',
		description='Empty',
		is_personal_group=True,
	)
	try:
		group.users.append(user)
		group.users.append(friend)
		await GroupManager.create(session, group)
	except IntegrityError:
		return
	chat = Chat(
		title=f'{user.name}:{user.id} and {friend.name}:{friend.id}',
		group=group,
	)
	await ChatManager.create(session, chat)
	await session.commit()


@router.post('/upload_avatar/{user_id}')
async def upload_avatar(
	session: Annotated[AsyncSession, Depends(get_async_session)],
	user_id: int,
	avatar: UploadFile,
):
	user = await UsrManager.get_one_by(session, id=user_id)
	created = datetime.datetime.utcnow()

	base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
	static_dir = os.path.join(base_dir, 'static')

	created = datetime.datetime.utcnow()
	path = os.path.join(static_dir, f'{created.year}/{created.month}/{created.day}')
	os.makedirs(path, exist_ok=True)

	file_path = os.path.join(path, avatar.filename)

	with open(file_path, 'wb+') as f:
		copyfileobj(avatar.file, f)

	user.avatar = file_path
	await session.commit()
