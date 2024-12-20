import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings
from database import Base
from auth.models import User, Token

# Create test database engine
test_engine = create_async_engine(settings.TEST_DB_URL)
async_session = async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.fixture(scope="session")
async def setup_database():
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop all tables after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def session(setup_database):
    async with async_session() as session:
        yield session
        # Rollback any changes made in the test
        await session.rollback()

@pytest.fixture
async def test_user(session):
    user = User(
        name="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
        is_active=True,
        is_verified=True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.fixture
async def test_token(session, test_user):
    token = Token(
        title="Test Token",
        token="test_token_string",
        user=test_user
    )
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token
