from sqlalchemy.ext.asyncio import AsyncSession
from db.dao import MessageManager
from db.models import Usr
from typing import Annotated
from fastapi import Depends
from db.database import get_async_session


async def get_no_read_messages(session: AsyncSession, user: Usr):
    messages = await MessageManager.get_all_messages_unread(session, user)
    return messages


# async def get_token
