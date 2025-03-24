from email import message
from sqlalchemy import delete, select, func, and_, or_
from sqlalchemy.sql.functions import user
from db.models import (
    RolePermission,
    RoleUsrGroup,
    Usr,
    Token,
    UsrGroup,
    Permission,
    Role,
    Group,
    Chat,
    Message,
    UsrReadedMessages,
)
from sqlalchemy.orm import joinedload
from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession
from chat.schemas import AllLastMessages
from logging_settings import get_logger
from db.database import Base
from db.error_handler import handle_error, MapNoResultFound


logger = get_logger(__name__)


class BaseManager(ABC):
    model = None

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_all(cls, session: AsyncSession):
        result = await session.execute(select(cls.model))
        result = result.scalars().all()
        return result

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_one_by(cls, session: AsyncSession, **filter):
        """Return one item or raise Exception"""
        result = await session.execute(select(cls.model).filter_by(**filter))
        result = result.scalars().one()
        return result

    @classmethod
    @handle_error()
    async def get_one_or_none_by(cls, session: AsyncSession, **filter):
        result = await session.execute(select(cls.model).filter_by(**filter))
        result = result.scalars().one_or_none()
        return result

    @classmethod
    async def get_filtered(cls, session: AsyncSession, **filter):
        result = await session.execute(select(cls.model).filter_by(**filter))
        result = result.scalars().all()
        return result

    @classmethod
    @handle_error(rollback=True)
    async def create(cls, session: AsyncSession, item):
        session.add(item)
        await session.commit()

    @classmethod
    @handle_error(rollback=True)
    async def create_all(cls, session: AsyncSession, items: list):
        session.add_all(items)
        await session.commit()

    @classmethod
    @handle_error(rollback=True)
    async def delete(cls, session: AsyncSession, item):
        await session.delete(item)
        await session.commit()

    @classmethod
    @handle_error(mapping_exception=[MapNoResultFound], rollback=True)
    async def delete_by(cls, session: AsyncSession, **filter):
        await session.execute(delete(cls.model).filter_by(**filter))
        await session.commit()


class UsrManager(BaseManager):
    model = Usr

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_groups(cls, session: AsyncSession, user: Usr):
        result = await session.execute(
            select(cls.model)
            .options(joinedload(cls.model.groups).joinedload(Group.chats))
            .where(cls.model.id == user.id)
        )
        result = result.scalars().first().groups
        return result

    @classmethod
    @handle_error([MapNoResultFound])
    async def search_users(cls, session: AsyncSession, field: str):
        result = await session.execute(
            select(Usr).where(
                or_(
                    field == str(cls.model.id),
                    field == cls.model.name,
                    field == cls.model.name_account,
                )
            )
        )
        result = result.scalars().all()
        return result

    # @classmethod
    # async def get_group_users(cls, session: AsyncSession, group_id: int):

    # @classmethod
    # async def get_chats_ids(cls, session: AsyncSession, user: Usr):
    #     try:
    #         result = await session.execute(
    #             select(cls.model)
    #                 .join(UsrGroup, UsrGroup.user_id==user.id)
    #                 .join(Group, Group.id == UsrGroup.group_id)
    #                 .join(Chat)
    #                 .where(cls.model.id == user.id
    #             )
    #         )
    #         result = result.scalars().first().groups
    #     except NoResultFound:
    #         raise HTTPException(status_code=404, detail="No result found")
    #     except Exception:
    #         raise HTTPException(status_code=500, detail="Unknown error occurred")
    #     return result


class TokenManager(BaseManager):
    model = Token

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_user_by_token(cls, session: AsyncSession, token: str):
        query = (
            select(cls.model)
            .options(joinedload(cls.model.user))
            .where(cls.model.token == token)
        )
        result = await session.execute(query)
        return result.scalars().one().user


class UsrGroupManager(BaseManager):
    model = UsrGroup

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_permissions(cls, session: AsyncSession, user_id: int, group_id: int):
        result = await session.execute(
            select(Permission.title)
            .join(
                cls.model,
                and_(
                    cls.model.user_id == user_id,
                    cls.model.group_id == group_id,
                ),
            )
            .join(RoleUsrGroup, RoleUsrGroup.usergroup_id == UsrGroup.id)
            .join(Role, Role.id == RoleUsrGroup.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .where(Permission.id == RolePermission.permission_id)
        )
        result = result.scalars().all()
        return result

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_roles(cls, session: AsyncSession, user_id: int):
        result = await session.execute(
            select(cls.model).where(cls.model.user_id == user_id)
        )
        roles = result.scalars().one().roles
        return roles

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_priority_role(cls, session: AsyncSession, user_id: int, group_id: int):
        result = await session.execute(
            select(func.min(Role.priority))
            .join(cls.model, cls.model.user_id == user_id)
            .join(
                RoleUsrGroup,
                and_(
                    RoleUsrGroup.usergroup_id == cls.model.id,
                    RoleUsrGroup.role_id == Role.id,
                ),
            )
            .filter(cls.model.group_id == group_id)
        )
        role_title = result.scalars().one()
        return role_title


class PermissionManager(BaseManager):
    model = Permission

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_permissions_in(cls, session: AsyncSession, list_items: list):
        result = await session.execute(
            select(cls.model).filter(cls.model.title.in_(list_items))
        )
        result = result.scalars().all()
        return result


class ChatManager(BaseManager):
    model = Chat


class GroupManager(BaseManager):
    model = Group

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_chats(cls, session: AsyncSession, group: Group):
        result = await session.execute(select(cls.model).where(cls.model.id == group.id))
        result = result.scalars().first().chats
        return result


class RoleManager(BaseManager):
    model = Role

    @classmethod
    @handle_error([MapNoResultFound])
    async def create(cls, session: AsyncSession, item: Role):
        max_priotrity = await session.execute(
            select(func.max(Role.priority)).where(Role.group_id == item.group_id)
        )
        max_priotrity = max_priotrity.scalar() or 0
        item.priority = max_priotrity + 1
        # commit inside
        await super().create(session, item)

    @classmethod
    @handle_error([MapNoResultFound])
    async def create_all(cls, session: AsyncSession, items: list, group_id):
        max_priotrity = await session.execute(
            select(func.max(Role.priority)).where(Role.group_id == group_id)
        )
        max_priotrity = max_priotrity.scalar() or 1
        for number, item in enumerate(items):
            item.priority = max_priotrity + number
        await super().create_all(session, items)


class MessageManager(BaseManager):
    model = Message

    @classmethod
    @handle_error([MapNoResultFound], rollback=True)
    async def create_message(
        cls,
        session: AsyncSession,
        user_id: int,
        chat_id: int,
        text: str,
    ):
        # Получаем максимальное значение local_id для текущей group_id
        result = await session.execute(
            select(cls.model.local_id)
            .where(cls.model.chat_id == chat_id)
            .order_by(cls.model.local_id.desc())
            .limit(1)
        )
        max_local_id = result.scalar() or 0  # Если записей нет, начнем с 0

        # Создаем новую запись с увеличенным local_id
        new_entry = cls.model(
            user_id=user_id,
            chat_id=chat_id,
            local_id=max_local_id + 1,
            text=text,
        )
        session.add(new_entry)
        await session.commit()
        await session.refresh(new_entry)
        return new_entry

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_chat_last_messages(
        cls, session: AsyncSession, chat_id: int, last_message_local_id: int
    ):
        """Return message autohr id and name"""
        result = await session.execute(
            select(cls.model, Usr.id, Usr.name)
            .join(Usr, Usr.id == cls.model.user_id)
            .where(cls.model.chat_id == chat_id)
            .where(cls.model.local_id > last_message_local_id)
            .order_by(cls.model.local_id)
        )
        result = result.all()
        return result

    @classmethod
    @handle_error([MapNoResultFound])
    async def get_all_messages_unread(cls, session: AsyncSession, user: Usr):
        result = await session.execute(
            select(cls.model)
            .select_from(cls.model)
            .join(UsrGroup, UsrGroup.user_id == user.id)
            .join(Group, Group.id == UsrGroup.group_id)
            .join(Chat, Chat.group_id == Group.id)
            .outerjoin(
                UsrReadedMessages,
                and_(
                    UsrReadedMessages.user_id == user.id,
                    UsrReadedMessages.message_id == cls.model.id,
                ),
            )
            .where(
                and_(
                    cls.model.chat_id == Chat.id,
                    UsrReadedMessages.id.is_(None),
                )
            )
        )
        result = result.scalars().all()
        for i in result:
            readed = UsrReadedMessages(message_id=i.id, user_id=user.id)
            await UsrReadedMessagesManager.create(session, readed)
        await session.commit()
        return result


class UsrReadedMessagesManager(BaseManager):
    model = UsrReadedMessages


class RoleUsrGroupManager(BaseManager):
    model = RoleUsrGroup
