from db.dao import GroupManager
from fastapi.testclient import TestClient
from main import app
import pytest


client = TestClient(app)


@pytest.mark.asyncio()
async def test_groups_me(session, test_user, test_token, load_seed_group):
    response = client.get('/api/groups/me', cookies={'access_token': test_token})
    assert response.status_code == 200
    assert response.json()


@pytest.mark.asyncio()
async def test_create_group(session, test_user, test_token):
    response = client.post(
        '/api/groups',
        cookies={'access_token': test_token},
        json={
            'title': 'GroupTestName',
            'description': 'Very good server for the best people',
        },
    )
    assert response.status_code == 200
    assert response.json()


@pytest.mark.parametrize('expected_status', [200, 403, 404])
async def test_patch_group(
    session,
    expected_status,
    test_token,
    load_seed_group,
    load_seed_roles,
    test_second_user,
):
    if expected_status == 200:
        response = client.patch(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_token},
            params={'title': 'GroupTestName'},
        )
        assert response.status_code == 200
        assert response.json()

    elif expected_status == 403:
        group = await GroupManager.get_one_by(session, id=load_seed_group.id)
        group.users.append(test_second_user[0])
        await session.commit()
        response = client.patch(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_second_user[1]},
            params={'title': 'GroupTestName'},
        )
        assert response.status_code == 403

    elif expected_status == 404:
        response = client.patch(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_second_user[1]},
            params={'title': 'GroupTestName'},
        )
        assert response.status_code == 404


@pytest.mark.parametrize('expected_status', [200, 404])
async def test_get_group(
    session,
    expected_status,
    test_user,
    test_token,
    load_seed_group,
    test_second_user,
):
    if expected_status == 200:
        response = client.get(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_token},
        )
        assert response.status_code == 200
        assert response.json()

    elif expected_status == 404:
        response = client.get(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_second_user[1]},
        )
        assert response.status_code == 404


@pytest.mark.parametrize('expected_status', [200, 403, 404])
async def test_delete_group(
    session,
    expected_status,
    test_user,
    test_token,
    load_seed_group,
    load_seed_roles,
    test_second_user,
):
    if expected_status == 200:
        response = client.delete(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_token},
        )
        assert response.status_code == 200
        with pytest.raises(Exception):
            await GroupManager.get_one_by(session, id=load_seed_group.id)

    elif expected_status == 403:
        group = await GroupManager.get_one_by(session, id=load_seed_group.id)
        group.users.append(test_second_user[0])
        await session.commit()
        response = client.delete(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_second_user[1]},
        )
        assert response.status_code == 403
        assert await GroupManager.get_one_by(session, id=load_seed_group.id)

    elif expected_status == 404:
        response = client.delete(
            f'/api/groups/{load_seed_group.id}',
            cookies={'access_token': test_second_user[1]},
        )
        assert response.status_code == 404
        assert await GroupManager.get_one_by(session, id=load_seed_group.id)


@pytest.mark.asyncio()
async def test_join_group(session, load_seed_group, test_second_user):
    response = client.post(
        f'/api/groups/join_group/{load_seed_group.id}',
        cookies={'access_token': test_second_user[1]},
    )
    assert response.status_code == 200


@pytest.mark.asyncio()
async def test_leave_group(session, load_seed_group, test_second_user):
    response1 = client.post(
        f'/api/groups/join_group/{load_seed_group.id}',
        cookies={'access_token': test_second_user[1]},
    )
    response2 = client.delete(
        f'/api/groups/leave_group/{load_seed_group.id}',
        cookies={'access_token': test_second_user[1]},
    )
    assert response2.status_code == 200
