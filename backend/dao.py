from email import message
from sqlalchemy import delete, select, func, and_, or_
from sqlalchemy.sql.functions import user
from models import (
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
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from types import NoneType
from chat.schemas import AllLastMessages
from logging_settings import get_logger


logger = get_logger(__name__)

class BaseManager(ABC):
	model = None

	@classmethod
	async def get_all(cls, session: AsyncSession):
		try:
			result = await session.execute(select(cls.model))
			result = result.scalars().all()
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result

	@classmethod
	async def get_one_by(cls, session: AsyncSession, **filter):
		try:
			result = await session.execute(select(cls.model).filter_by(**filter))
			result = result.scalars().one()
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found (get_one_by)')
		except Exception as e:
			raise HTTPException(status_code=500, detail='Unknown error occurred' + str(e))
		return result

	@classmethod
	async def get_filtered(cls, session: AsyncSession, **filter):
		try:
			result = await session.execute(select(cls.model).filter_by(**filter))
			result = result.scalars().all()
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result

	@classmethod
	async def create(cls, session: AsyncSession, item):
		try:
			session.add(item)
		except Exception:
			await session.rollback()
			raise HTTPException(status_code=500, detail=f'{cls.model} add error')

	@classmethod
	async def create_all(cls, session: AsyncSession, items: list):
		try:
			session.add_all(items)
		except Exception:
			await session.rollback()
			raise HTTPException(status_code=500, detail=f'{cls.model} add error')

	@classmethod
	async def delete(cls, session: AsyncSession, item):
		try:
			await session.delete(item)
		except Exception:
			await session.rollback()
			raise HTTPException(status_code=500, detail=f'{cls.model} delete error')

	@classmethod
	async def delete_by(cls, session: AsyncSession, **filter):
		try:
			await session.execute(delete(cls.model).filter_by(**filter))
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found (delete_by)')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')


class UsrManager(BaseManager):
	model = Usr

	@classmethod
	async def get_one_by(cls, session: AsyncSession, **filter):
		try:
			result = await session.execute(select(cls.model).filter_by(**filter))
			result = result.scalars().one()
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result

	@classmethod
	async def get_groups(cls, session: AsyncSession, user: Usr):
		try:
			result = await session.execute(
				select(cls.model)
				.options(joinedload(cls.model.groups).joinedload(Group.chats))
				.where(cls.model.id == user.id)
			)
			result = result.scalars().first().groups
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result

	@classmethod
	async def search_users(cls, session: AsyncSession, field: str):
		try:
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
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception as e:
			logger.debug(e)
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result

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
	async def get_user_by_token(cls, session: AsyncSession, token: str):
		try:
			query = (
				select(cls.model)
				.options(joinedload(cls.model.user))
				.where(cls.model.token == token)
			)
			result = await session.execute(query)
			return result.scalars().one().user
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')


class UsrGroupManager(BaseManager):
	model = UsrGroup

	@classmethod
	async def get_permissions(
		cls, session: AsyncSession, user_id: int | Usr, group_id: int
	):
		if isinstance(user_id, Usr):
			user_id = user_id.id
		try:
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
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result

	@classmethod
	async def get_roles(cls, session: AsyncSession, user_id: int | Usr):
		if isinstance(user_id, Usr):
			user_id = user_id.id
		try:
			result = await session.execute(
				select(cls.model).where(cls.model.user_id == user_id)
			)
			roles = result.scalars().one().roles
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return roles

	@classmethod
	async def get_priority_role(
		cls, session: AsyncSession, user_id: int | Usr, group_id: int
	):
		if isinstance(user_id, Usr):
			user_id = user_id.id
		try:
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
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception as e:
			print(e)
			raise HTTPException(status_code=500, detail='Unknown error occurred')

		return role_title


class PermissionManager(BaseManager):
	model = Permission

	@classmethod
	async def get_permissions_in(cls, session: AsyncSession, list_items: list):
		try:
			result = await session.execute(
				select(cls.model).filter(cls.model.title.in_(list_items))
			)
			result = result.scalars().all()
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result


class ChatManager(BaseManager):
	model = Chat


class GroupManager(BaseManager):
	model = Group

	@classmethod
	async def get_chats(cls, session: AsyncSession, group: Group):
		try:
			result = await session.execute(
				select(cls.model).where(cls.model.id == group.id)
			)
			result = result.scalars().first().chats
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result


class RoleManager(BaseManager):
	model = Role

	@classmethod
	async def create(cls, session: AsyncSession, item: Role):
		max_priotrity = await session.execute(
			select(func.max(Role.priority)).where(Role.group_id == item.group_id)
		)
		max_priotrity = max_priotrity.scalar() or 0
		item.priority = max_priotrity + 1
		await super().create(session, item)

	@classmethod
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
	async def create_message(
		cls,
		session: AsyncSession,
		user_id: int,
		chat_id: int,
		text: str,
		id: int | None = None,
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
			id=id,
			user_id=user_id,
			chat_id=chat_id,
			local_id=max_local_id + 1,
			text=text,
		)
		session.add(new_entry)
		return new_entry

	@classmethod
	async def get_chat_last_messages(
		cls, session: AsyncSession, chat_id: int, last_message_local_id: int
	):
		try:
			result = await session.execute(
				select(cls.model, Usr.name)
				.join(Usr, Usr.id == cls.model.user_id)
				.where(cls.model.chat_id == chat_id)
				.where(cls.model.local_id > last_message_local_id)
				.order_by(cls.model.local_id)
			)
			result = result.all()
		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result

	@classmethod
	async def get_all_messages_unread(cls, session: AsyncSession, user: Usr):
		try:
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

		except NoResultFound:
			raise HTTPException(status_code=404, detail='No result found')
		except Exception:
			raise HTTPException(status_code=500, detail='Unknown error occurred')
		return result


class UsrReadedMessagesManager(BaseManager):
	model = UsrReadedMessages
