import pytest
from auth.utils import (
    verify_token,
    get_token,
    get_hashed_password,
    verify_password,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    list_permissions,
    my_list_permissions,
    my_priority_role,
    get_list_permissions_in,
)
from datetime import timedelta
from fastapi import HTTPException


@pytest.mark.parametrize(
    'token, expected_status',
    [
        ('test_token_string', 200),
        ('invalid_token', 404),
    ],
)
async def test_verify_token(session, test_token, token, expected_status):
    if expected_status == 200:
        token = await verify_token(token, session)
        assert token == test_token

    elif expected_status == 404:
        with pytest.raises(HTTPException) as exc:
            await verify_token(token, session)
        assert exc.value.status_code == expected_status


@pytest.mark.asyncio()
async def test_get_hashed_password():
    password = 'testpassword'
    hashed = get_hashed_password(password)
    assert verify_password(password, hashed)


@pytest.mark.asyncio()
async def test_verify_password():
    password = 'testpassword'
    hashed = get_hashed_password(password)
    assert verify_password(password, hashed)
    assert not verify_password('wrongpassword', hashed)


@pytest.mark.parametrize(
    'email, password, expected_status',
    [
        ('test@example.com', 'password', 200),
        ('test@example.com', 'wrongpassword', 401),
        ('NoInDB@example.com', 'password', 404),
    ],
)
async def test_authenticate_user(session, test_user, email, password, expected_status):
    if expected_status == 200:
        user = await authenticate_user(email=email, password=password, session=session)
        assert user.email == test_user.email

    elif expected_status == 401:
        with pytest.raises(HTTPException) as exc:
            await authenticate_user(email=email, password=password, session=session)
        assert exc.value.status_code == 401

    elif expected_status == 404:
        with pytest.raises(HTTPException) as exc:
            await authenticate_user(email=email, password=password, session=session)
        assert exc.value.status_code == 404


@pytest.mark.asyncio()
async def test_create_access_token(session, test_user):
    data = {'sub': test_user.email}
    token = await create_access_token(session, test_user, data)
    assert token is not None


@pytest.mark.parametrize(
    'token, expected_status',
    [
        ('test_token_string', 200),
        ('invalid_token', 404),
    ],
)
async def test_get_current_user(token, expected_status, session, test_user, test_token):
    if expected_status == 200:
        user = await get_current_user(session, token)
        assert user.email == test_user.email

    elif expected_status == 401:
        with pytest.raises(HTTPException) as exc:
            await get_current_user(session, token)
        assert exc.value.status_code == expected_status

    elif expected_status == 404:
        with pytest.raises(HTTPException) as exc:
            await get_current_user(session, token)
        assert exc.value.status_code == expected_status


async def test_get_current_active_user(session, test_user):
    assert await get_current_active_user(test_user)


@pytest.mark.asyncio()
async def test_list_permissions(session, test_user, load_seed_roles, load_seed_group):
    permissions = await list_permissions(
        session, user_id=test_user.id, group_id=load_seed_group.id
    )
    assert permissions


@pytest.mark.asyncio()
async def test_get_list_permissions_in(session, load_seed_permissions):
    permissions = await get_list_permissions_in(
        session=session, permissions=['can_edit_role']
    )
    for perm in permissions:
        assert perm.title == 'can_edit_role'


@pytest.mark.asyncio()
async def test_my_priority_role(session, test_user, load_seed_roles):
    role = await my_priority_role(session, test_user, 1)
    assert role
