from config import settings
from fastapi.testclient import TestClient
from main import app
import pytest


client = TestClient(app)


@pytest.mark.parametrize(
    'email, password, expected_status',
    [
        ('test@example.com', 'password', 200),
        ('NoInDB@example.com', 'password', 404),
    ],
)
async def test_login(session, test_user, email, password, expected_status):
    response = client.post('/api/auth/login', data={'email': email, 'password': password})
    assert response.status_code == expected_status


@pytest.mark.asyncio()
async def test_get_token(session, test_user, test_token):
    response = client.get('/api/auth/get_token', cookies={'access_token': test_token})
    assert response.status_code == 200


@pytest.mark.asyncio()
async def test_permissions(session, test_user, load_seed_group, load_seed_roles):
    permissions = client.get(
        '/api/auth/permissions',
        params={'user_id': test_user.id, 'group_id': load_seed_group.id},
    )
    assert permissions.json()


# @pytest.mark.parametrize("email, password, expected_status", [
#     ("test@example.com", "password", 200),
#     ("NoInDB@example.com", "password", 404),
# ])
# async def test_users_me(session, test_user, email, password, expected_status):
#     token_response = client.post('/api/auth/login', data={"email": email, "password": password})
#     if token_response.status_code != 200:
#         assert token_response.status_code == expected_status
#     else:
#         response = client.get('/api/auth/users/me', cookies={"access_token": token_response.json()})
#         assert response.status_code == expected_status
