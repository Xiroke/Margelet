from sqlalchemy import insert, select
from abc import ABC
from sqlalchemy.exc import NoResultFound
from exceptions import HTTPNoResultFound, HTTPUnknownException
from sqlalchemy.ext.asyncio import AsyncSession


class BaseManager(ABC):
    model = None

    @classmethod
    async def add(cls, session: AsyncSession, item):
        try:
            session.add(item)
            await session.commit()
            return item
        except Exception as e:
            await session.rollback()
            raise e

    @classmethod
    async def create_values(cls, session: AsyncSession, *args):
        query = insert(cls.model).values(*args) 
        result = await session.execute(query)
        await session.commit()
        return result
    
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
