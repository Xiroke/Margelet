from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import create_access_token, get_hashed_password
from config import settings
from db.dao import (
    ChatManager,
    GroupManager,
    MessageManager,
    PermissionManager,
    RoleManager,
    UsrGroupManager,
    UsrManager,
    TokenManager,
    RoleUsrGroupManager,
)
from db.models import Chat, Group, Permission, Role, Usr
from logging_settings import get_logger


logger = get_logger(__name__)
# admin = "admin"
# CAN_EDIT_ROLE = "can_edit_role"
# CAN_CREATE_GROUP = "can_create_group"
# CAN_EDIT_MAIN_INFO_GROUP = "can_edit_main_info_group"
# CAN_CREATE_CHAT = "can_create_chat"
# CAN_EDIT_CHAT = "can_edit_chat"
# CAN_DELETE_CHAT = "can_delete_chat"


async def seed_permissions(session: AsyncSession):
    try:
        session.add_all(
            [
                Permission(title='admin'),
                Permission(title='can_edit_role'),
                Permission(title='can_create_group'),
                Permission(title='can_edit_main_info_group'),
                Permission(title='can_create_chat'),
                Permission(title='can_edit_chat'),
                Permission(title='can_delete_chat'),
            ]
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()


async def seed_admin(session: AsyncSession):
    existing_admin = await UsrManager.get_one_or_none_by(
        session, email=settings.ADMIN_EMAIL
    )

    if existing_admin:
        return existing_admin

    hashed_password = get_hashed_password(settings.ADMIN_PASSWORD)
    admin = Usr(
        name=settings.ADMIN_NAME,
        name_account=settings.ADMIN_NAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    test = Usr(
        name='test',
        name_account='test',
        email='test@test.com',
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )

    await UsrManager.create(session, admin)
    await UsrManager.create(session, test)
    await session.commit()
    return admin


class TestSeed:
    @staticmethod
    async def create_group(session: AsyncSession, user: Usr):
        if not user:
            raise ValueError('Usr must be provided (create_group)')

        existing_gp1 = await GroupManager.get_one_or_none_by(
            session, title='Test Group 1'
        )
        if existing_gp1:
            return existing_gp1

        gp1 = Group(
            title='Test Group 1',
            description='Test Group 1 Description',
            is_personal_group=False,
        )
        gp1.users.append(user)
        await GroupManager.create(session, gp1)
        await session.commit()
        return gp1

    @staticmethod
    async def create_chats(session: AsyncSession, group: Group):
        exicsing_chats = await ChatManager.get_filtered(session, group_id=group.id)
        if exicsing_chats:
            return exicsing_chats

        chats = [
            Chat(title='Test Chat 1', group_id=group.id),
            Chat(title='Test Chat 2', group_id=group.id),
        ]
        await ChatManager.create_all(session, chats)
        await session.commit()
        return chats

    @staticmethod
    async def create_messages(session: AsyncSession, user_id: int):
        messages = await MessageManager.get_filtered(session, chat_id=1)
        messages2 = await MessageManager.get_filtered(session, chat_id=2)
        if messages and messages2:
            return

        try:
            await MessageManager.create_message(
                session, user_id=user_id, chat_id=1, text='Test Message 1'
            )
            await MessageManager.create_message(
                session, user_id=user_id, chat_id=1, text='Test Message 2'
            )
            await MessageManager.create_message(
                session, user_id=user_id, chat_id=1, text='Test Message 3'
            )
            await MessageManager.create_message(
                session, user_id=user_id, chat_id=1, text='Test Message 4'
            )
            await MessageManager.create_message(
                session, user_id=user_id, chat_id=1, text='Test Message 5'
            )
            await MessageManager.create_message(
                session, user_id=user_id, chat_id=2, text='Test Message 1'
            )
            await session.commit()
        except IntegrityError:
            await session.rollback()

    @staticmethod
    async def create_roles(session: AsyncSession, group: Group, user: Usr):
        if not group or not user:
            raise ValueError('Group and user must be provided (create_roles)')

        usergroup = await UsrGroupManager.get_one_by(
            session, user_id=user.id, group_id=group.id
        )
        role = await RoleManager.get_one_or_none_by(
            session, title='Admin', group_id=group.id
        )
        if role:
            return
            # existing_roles = await RoleUsrGroupManager.get_one_or_none_by(session, usergroup_id=usergroup.id, role_id=role.id)

            # if existing_roles:
            # return

        admin_permissions = await PermissionManager.get_all(session)
        role_admin = Role(title='Admin', group_id=group.id)
        await RoleManager.create(session, role_admin)
        await session.refresh(role_admin)
        role_admin.permissions = admin_permissions

        usergroup.roles.append(role_admin)
        await session.commit()

    @staticmethod
    async def create_bot(session: AsyncSession):
        existing_bot = await UsrManager.get_one_or_none_by(
            session, name_account='TestBot'
        )

        if existing_bot:
            token = await create_access_token(
                session, existing_bot, data={'email': existing_bot.email}
            )
            return existing_bot

        hashed_password = get_hashed_password('test_password')
        bot_user = Usr(
            name='TestBot',
            name_account='TestBot',
            email='TestBot' + '@margelet.bot',
            hashed_password=hashed_password,
            is_bot=True,
        )

        await UsrManager.create(session, bot_user)
        await session.commit()
        token = await create_access_token(
            session, bot_user, data={'email': bot_user.email}
        )
        return token
