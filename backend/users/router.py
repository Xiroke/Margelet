import io
from fastapi import APIRouter, Depends, HTTPException, status
from db.models import Group, Usr, Chat
from db.dao import UsrManager, GroupManager, ChatManager
from db.database import get_async_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from auth.schemas import UsrRead
from typing import List
from fastapi import UploadFile
from fastapi.responses import FileResponse
import datetime
from shutil import copyfileobj
import os
from auth.utils import get_current_active_user
from logging_settings import get_logger
from PIL import Image
from utils import save_image_static


router = APIRouter(prefix='/api/users', tags=['users'])
logger = get_logger(__name__)


@router.get('/search/{field}')
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


@router.get('/avatar')
async def load_avatar_to_user(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_id: int | None = None,
    user_name_account: str | None = None,
):
    if user_id:
        user = await UsrManager.get_one_by(session, id=user_id)
    elif user_name_account:
        user = await UsrManager.get_one_by(session, name_account=user_name_account)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You must provide user_id or user_name_account',
        )

    if not user.avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Avatar not found',
        )

    return FileResponse(user.avatar)


@router.get('/avatar/me')
async def load_avatar_me(
    user: Annotated[Usr, Depends(get_current_active_user)],
):
    return FileResponse(user.avatar)


@router.post('/avatar/me')
async def upload_avatar_me(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    avatar: UploadFile,
):
    user: Usr = await UsrManager.get_one_by(session, id=user.id)

    path = './static/avatars'

    file_path = await save_image_static(
        path_to_file=path, filename=str(user.id), image=avatar
    )
    user.avatar = file_path
    await session.commit()
