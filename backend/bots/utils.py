from sqlalchemy.ext.asyncio import AsyncSession
from dao import MessageManager
from models import User
from typing import Annotated
from fastapi import Depends
from database import get_async_session


async def get_no_read_messages(session: AsyncSession, user: User):
	messages = await MessageManager.get_all_messages_unread(session, user)
	return messages

# async def get_token