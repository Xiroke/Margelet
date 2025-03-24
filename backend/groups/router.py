import datetime
import io
import os
from shutil import copyfileobj
from fastapi import APIRouter, Depends, Response, Body, UploadFile
from fastapi import status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from db.models import Usr, Group, Role, UsrGroup
from auth.utils import get_current_active_user
from db.dao import GroupManager, UsrGroupManager, UsrManager, RoleManager
from db.database import get_async_session
from auth.utils import get_token, my_list_permissions, my_priority_role
from auth.schemas import PermissionEnum
from .schemas import GroupCreate, GroupRead
from sqlalchemy.exc import IntegrityError
from db.shortcuts import get_all_permissions
from PIL import Image
from logging_settings import get_logger
from utils import save_image_static


logger = get_logger(__name__)

router = APIRouter(prefix='/api/groups', tags=['groups'])


@router.get('/me')
async def get_groups_me(
    user: Annotated[Usr, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> List[GroupRead]:
    groups = await UsrManager.get_groups(session, user)
    return groups


@router.post('')
async def create_group(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    group: Annotated[GroupCreate, Body()],
):
    try:
        group = Group(title=group.title, description=group.description)
        group.users.append(user)
        await GroupManager.create(session, group)
        await session.refresh(group)

        role_creator = Role(title='Creator', group_id=group.id)
        role_creator.permissions = await get_all_permissions(session)
        await RoleManager.create(session, role_creator)
        await session.refresh(role_creator)

        usergroup: UsrGroup = await UsrGroupManager.get_one_by(
            session, user_id=user.id, group_id=group.id
        )
        usergroup.roles.append(role_creator)
        await session.commit()

        return group

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/{group_id}')
async def get_group(
    user: Annotated[Usr, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    group_id: int,
):
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

    groups = await GroupManager.get_one_by(session, id=group_id)
    return groups


@router.patch('/{group_id}')
async def patch_group(
    user: Annotated[str, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    group_id: int,
    title: str | None = None,
    description: str | None = None,
):
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

    my_permissions = await my_list_permissions(session, user, group_id)
    if 'can_edit_main_info_group' not in my_permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    group = await GroupManager.get_one_by(session, id=group_id)
    if title is not None:
        group.title = title
    if description is not None:
        group.description = description
    await session.commit()
    return group


@router.delete('/{group_id}')
async def delete_group(
    user: Annotated[str, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    group_id: int,
):
    # raise 404 if user not in group
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

    my_permissions = await my_list_permissions(session, user, group_id)
    if 'admin' not in my_permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await GroupManager.delete_by(session, id=group_id)
    await session.commit()


@router.post('/join_group/{group_id}')
async def join_group(
    user: Annotated[Usr, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    group_id: int,
):
    usergroup = UsrGroup(user_id=user.id, group_id=group_id)
    await UsrGroupManager.create(session, usergroup)
    await session.commit()
    return {'status': status.HTTP_201_CREATED}


@router.delete('/leave_group/{group_id}')
async def leave_group(
    user: Annotated[Usr, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    group_id: int,
):
    await UsrGroupManager.delete_by(session, user_id=user.id, group_id=group_id)
    await session.commit()
    return {'status': status.HTTP_204_NO_CONTENT}


@router.post('/roles/{group_id}')
async def create_role(
    my_permissions: Annotated[str, Depends(my_list_permissions)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    group_id: int,
    title: str,
    role_permissions: List[PermissionEnum],
):
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

    if PermissionEnum.CAN_EDIT_ROLE not in my_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied'
        )

    group = await GroupManager.get_one_by(session, id=group_id)
    role = Role(title=title, group_id=group.id)
    role.permissions.extend(role_permissions)

    await RoleManager.add(session, role)
    await session.commit()
    return {'status': status.HTTP_201_CREATED}


@router.get('/roles/{group_id}')
async def get_roles(
    session: Annotated[AsyncSession, Depends(get_async_session)], group_id: int
):
    roles = await RoleManager.get_one_by(session=session, group_id=group_id)
    return roles


@router.delete('/roles/{group_id}')
async def delete_role(
    my_permissions: Annotated[str, Depends(my_list_permissions)],
    my_priority_role: Annotated[Role, Depends(my_priority_role)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    group_id: int,
    role_id: int,
):
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)

    if PermissionEnum.CAN_EDIT_ROLE not in my_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Permission denied'
        )

    role = await RoleManager.get_one_by(session, id=role_id)
    await RoleManager.delete(session, role)
    await session.commit()
    return {'status': status.HTTP_204_NO_CONTENT}


@router.get('/group_avatar/{group_id}')
async def load_avatar_group(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    group_id: int,
):
    # check if user in group
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)
    group = await GroupManager.get_one_by(session, id=group_id)

    return FileResponse(group.avatar)


@router.post('/group_avatar/{group_id}')
async def upload_avatar_group(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    avatar: UploadFile,
    group_id: int,
):
    # check if user in group
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)
    group = await GroupManager.get_one_by(session, id=group_id)

    path = './static/group_avatars'

    file_path = await save_image_static(
        path_to_file=path, filename=str(group_id), image=avatar
    )
    group.avatar = file_path
    await session.commit()


@router.get('/group_panorama/{group_id}')
async def load_panorama_group(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    group_id: int,
):
    # check if user in group
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)
    group = await GroupManager.get_one_by(session, id=group_id)

    if not group.panorama:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Panorama not found'
        )

    return FileResponse(group.panorama)


@router.post('/group_panorama/{group_id}')
async def upload_panorama_group(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[Usr, Depends(get_current_active_user)],
    panorama: UploadFile,
    group_id: int,
):
    # check if user in group
    await UsrGroupManager.get_one_by(session, user_id=user.id, group_id=group_id)
    group = await GroupManager.get_one_by(session, id=group_id)

    path = './static/group_panorama'

    file_path = await save_image_static(
        path_to_file=path, filename=str(group_id), image=panorama
    )
    group.panorama = file_path
    await session.commit()
