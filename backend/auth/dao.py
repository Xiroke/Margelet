from  dao import BaseManager
from .models import User, Token, Message, Group, Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.exc import NoResultFound
from exceptions import HTTPNoResultFound, HTTPUnknownException


class UserManager(BaseManager):
    model = User

    @classmethod
    async def get_one_by(cls, session: AsyncSession, **filter):
        try:
            result = await session.execute(select(cls.model).filter_by(**filter))
            result = result.scalars().one()
        except NoResultFound:
            raise HTTPNoResultFound()
        except Exception:
            raise HTTPUnknownException()
        return result

    @classmethod
    async def get_groups(cls, session: AsyncSession, user: User):
        try:
            result = await session.execute(select(cls.model).options(joinedload(cls.model.groups)).where(cls.model.id == user.id))
            result = result.scalars().first().groups
        except NoResultFound:
            raise HTTPNoResultFound()
        except Exception:
            raise HTTPUnknownException()
        return result

class TokenManager(BaseManager):
    model = Token

    @classmethod
    async def get_user_by_token(cls, session: AsyncSession, token: str):
        query = select(cls.model).options(joinedload(cls.model.user)).where(cls.model.token == token)
        result = await session.execute(query)
        return result.scalars().one_or_none().user

class MessageMenager(BaseManager):
    model = Message

    @classmethod
    async def add_message(cls, session: AsyncSession, user_id: int, chat_id: int, message: str):
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
            message=message
        )
        session.add(new_entry)
        await session.commit()

    async def get_messages(cls, session: AsyncSession, chat_id: int):
        try:
            result = await session.execute(select(cls.model).where(cls.model.chat_id == chat_id).order_by(cls.model.local_id.desc()).distinct().limit(30))
            result = result.scalars().all()
        except NoResultFound:
            raise HTTPNoResultFound()
        except Exception:
            raise HTTPUnknownException()
        return result

class GroupManager(BaseManager):
    model = Group

    @classmethod
    async def get_chats(cls, session: AsyncSession, group: Group):
        try:
            result = await session.execute(select(cls.model).options(joinedload(cls.model.chats)).where(cls.model.id == group.id))
            result = result.scalars().first().chats
        except NoResultFound:
            raise HTTPNoResultFound()
        except Exception:
            raise HTTPUnknownException()
        return result

class ChatManager(BaseManager):
    model = Chat