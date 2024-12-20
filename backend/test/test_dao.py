import pytest
from auth.models import User, Token
from auth.dao import UserManager, TokenManager
from exceptions import HTTPNoResultFound

pytest_plugins = ('pytest_asyncio',)

# Test User Manager
@pytest.mark.asyncio
async def test_add_user(session):
    # Arrange
    new_user = User(
        name="test_add_user",
        email="test_add_user@example.com",
        hashed_password="test_add_user",
        is_active=True
    )
    
    # Act
    result = await UserManager.add(session, new_user)
    
    # Assert
    assert result.id is not None
    assert result.email == "new_test_add@example.com"
    assert result.name == "newuser"

@pytest.mark.asyncio
async def test_get_one_by_user(session):
    # Arrange
    user = User(
        name="test_get_one_by_user",
        email="test_get_one_by_user@example.com",
        hashed_password="test_get_one_by_user",
        is_active=True,
        is_verified=True
    )
    await UserManager.add(session, user)
    
    # Act
    result = await UserManager.get_one_by(session, email=user.email)
    
    # Assert
    assert result.id == user.id
    assert result.email == user.email

@pytest.mark.asyncio
async def test_get_one_by_user_not_found(session):
    # Act & Assert
    with pytest.raises(HTTPNoResultFound):
        await UserManager.get_one_by(session, email="nonexistent@example.com")

# Test Token Manager
@pytest.mark.asyncio
async def test_add_token(session):
    # Arrange
    user = User(
        name="test_add_token",
        email="test_add_token@example.com",
        hashed_password="test_add_token",
        is_active=True,
        is_verified=True
    )
    await UserManager.add(session, user)
    
    new_token = Token(
        title="test_add_token_Token",
        token="test_add_token_string",
        user=user
    )
    
    # Act
    result = await TokenManager.add(session, new_token)
    
    # Assert
    assert result.id is not None
    assert result.token == "new_test_token_string"
    assert result.user_id == user.id

@pytest.mark.asyncio
async def test_get_one_by_token(session):
    # Arrange
    user = User(
        name="test_get_one_by_token",
        email="test_get_one_by_token@example.com",
        hashed_password="test_get_one_by_token",
        is_active=True,
        is_verified=True
    )
    await UserManager.add(session, user)
    
    token = Token(
        title="Test Token",
        token="test_token_string_get",
        user=user
    )
    await TokenManager.add(session, token)
    
    # Act
    result = await TokenManager.get_one_by(session, token=token.token)
    
    # Assert
    assert result.id == token.id
    assert result.token == token.token

@pytest.mark.asyncio
async def test_get_one_by_token_not_found(session):
    # Act & Assert
    with pytest.raises(HTTPNoResultFound):
        await TokenManager.get_one_by(session, token="nonexistent_token")