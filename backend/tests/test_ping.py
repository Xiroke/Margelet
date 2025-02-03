from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


async def test_get_ping():
	response = client.get('/api/ping')
	assert response.status_code == 200
	assert response.json() == 'pong'


async def test_post_ping():
	response = client.post('/api/ping', params={'number': 1})
	assert response.status_code == 200
	assert response.json() == 1
