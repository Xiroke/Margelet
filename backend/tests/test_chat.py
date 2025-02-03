from config import settings
from fastapi.testclient import TestClient
from main import app
import pytest


client = TestClient(app)


@pytest.mark.asyncio()
async def test_chat_last_messages(
	session,
	load_seed_group,
	test_user,
	load_seed_chats,
	load_seed_messages,
	test_token,
):
	response = client.get(
		f'/api/chat/chat_last_messages/{load_seed_group.id}/{load_seed_chats[0].id}',
		params={'last_message_local_id': 1},
		cookies={'access_token': test_token},
	)
	assert response.status_code == 200
	data = response.json()
	assert data[0]['local_id'] == 2
