from dao import UsrReadedMessagesManager
from models import UsrReadedMessages
from config import settings
from fastapi.testclient import TestClient
from bots.router import app
import pytest


client = TestClient(app)


@pytest.mark.asyncio()
async def test_no_read_messages(
	session, load_seed_group, load_seed_messages, test_bot, test_bot_token
):
	load_seed_group.users.append(test_bot)
	await session.commit()
	await UsrReadedMessagesManager.create(
		session, UsrReadedMessages(user_id=test_bot.id, message_id=1)
	)
	await session.commit()
	response = client.get('/no_read_messages', cookies={'access_token': test_bot_token})
	assert response.status_code == 200
	assert response.json()
	response = client.get('/no_read_messages', cookies={'access_token': test_bot_token})
	assert not response.json()
