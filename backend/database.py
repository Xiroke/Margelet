from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings


class Base(DeclarativeBase):
	pass


DATABASE_URL = settings.DB_URL
# engine = create_engine('postgresql+asyncpg://user:password@host:port/name')

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)


async def get_async_session():
	session = async_session_maker()
	try:
		yield session
	finally:
		await session.close()
