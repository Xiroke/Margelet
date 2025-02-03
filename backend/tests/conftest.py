from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings
from database import Base
from auth.utils import get_hashed_password
from models import Usr, Token
import pytest_asyncio
from seed import seed_permissions, TestSeed

# Create test database engine
test_engine = create_async_engine(settings.TEST_DB_URL)
async_session = async_sessionmaker(test_engine, expire_on_commit=False)
Base.metadata.bind = test_engine


@pytest_asyncio.fixture(scope='function')
async def setup_database():
	async with test_engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)
	yield

	async with test_engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def session(setup_database):
	async with async_session() as session:
		yield session


@pytest_asyncio.fixture(scope='function')
async def test_user(session):
	user = Usr(
		name='testuser',
		email='test@example.com',
		name_account='testuser',
		hashed_password=get_hashed_password('password'),
		is_active=True,
		is_verified=True,
	)
	session.add(user)
	await session.commit()
	yield user


@pytest_asyncio.fixture(scope='function')
async def test_second_user(session):
	user = Usr(
		name='testseconduser',
		email='test_second@example.com',
		name_account='testseconduser',
		hashed_password=get_hashed_password('password'),
		is_active=True,
		is_verified=True,
	)
	session.add(user)
	await session.flush()
	token = Token(title='Test Token', token='test_token_string2', user=user)
	session.add(token)
	await session.commit()
	yield user, token.token


@pytest_asyncio.fixture(scope='function')
async def test_token(session, test_user):
	token = Token(title='Test Token', token='test_token_string', user=test_user)
	session.add(token)
	await session.commit()
	yield token.token


@pytest_asyncio.fixture(scope='function')
async def load_seed_permissions(session):
	await seed_permissions(session)
	await session.commit()
	yield


@pytest_asyncio.fixture(scope='function')
async def load_seed_group(session, test_user):
	group = await TestSeed.create_group(session, test_user)
	await session.commit()
	yield group


@pytest_asyncio.fixture(scope='function')
async def load_seed_chats(session, load_seed_group):
	chats = await TestSeed.create_chats(session)
	await session.commit()
	yield chats


@pytest_asyncio.fixture(scope='function')
async def load_seed_roles(session, test_user, load_seed_group, load_seed_permissions):
	await TestSeed.create_roles(session, load_seed_group, test_user)
	await session.commit()
	yield


@pytest_asyncio.fixture(scope='function')
async def load_seed_messages(session, test_user, load_seed_chats, load_seed_roles):
	await TestSeed.create_messages(session, test_user.id)
	await session.commit()
	yield


@pytest_asyncio.fixture(scope='function')
async def test_bot(session):
	bot = Usr(
		name='bot',
		email='bot@example.com',
		name_account='testbot',
		hashed_password=get_hashed_password('password'),
		is_active=True,
		is_verified=True,
		is_bot=True,
	)
	session.add(bot)
	await session.commit()
	yield bot


@pytest_asyncio.fixture(scope='function')
async def test_bot_token(session, test_bot):
	token = Token(title='Test Token', token='test_token_string34', user=test_bot)
	session.add(token)
	await session.commit()
	yield token.token
